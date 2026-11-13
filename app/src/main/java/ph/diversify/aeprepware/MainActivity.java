package ph.diversify.aeprepware;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.graphics.Color;
import android.webkit.*;
import android.view.View;
import android.view.WindowInsets;
import android.widget.FrameLayout;
import android.widget.Toast;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;

/** Local-only origin: remote pages never receive the export/import bridge. */
public final class MainActivity extends Activity {
    private static final String ORIGIN = "https://appassets.androidplatform.net";
    private WebView web;
    private String pendingExport;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        // Inset a native parent, not WebView padding: CSS fixed navigation must
        // use a viewport that ends above Android's gesture/three-button bar.
        if (Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(false);
        else getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR |
            View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        FrameLayout content = new FrameLayout(this);
        web = new WebView(this);
        content.addView(web, new FrameLayout.LayoutParams(-1, -1));
        setContentView(content);
        content.setOnApplyWindowInsetsListener((view, insets) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                int bottom = Math.max(bars.bottom, insets.getInsets(WindowInsets.Type.ime()).bottom);
                view.setPadding(bars.left, bars.top, bars.right, bottom);
                return WindowInsets.CONSUMED;
            }
            view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        content.requestApplyInsets();
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSafeBrowsingEnabled(true);
        web.addJavascriptInterface(new FilesBridge(), "AndroidFiles");
        web.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                Uri uri = req.getUrl();
                if (!ORIGIN.equals(uri.getScheme()+"://"+uri.getAuthority())) return null;
                String path = uri.getPath();
                if (path == null || path.equals("/")) path = "/index.html";
                if (!path.matches("/[a-zA-Z0-9_.-]+")) return new WebResourceResponse("text/plain", "UTF-8", new ByteArrayInputStream(new byte[0]));
                String mime = path.endsWith(".js") ? "application/javascript" : path.endsWith(".css") ? "text/css" : path.endsWith(".json") ? "application/json" : "text/html";
                try { return new WebResourceResponse(mime, "UTF-8", getAssets().open(path.substring(1))); }
                catch (IOException ex) { return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", null, new ByteArrayInputStream(new byte[0])); }
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                if (req.getUrl().toString().startsWith(ORIGIN+"/")) return false;
                if ("https".equals(req.getUrl().getScheme())) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, req.getUrl())); }
                    catch (android.content.ActivityNotFoundException ex) { toast("No browser is available."); }
                }
                return true;
            }
        });
        web.loadUrl(ORIGIN+"/index.html");
    }
    private void toast(String text) { runOnUiThread(() -> Toast.makeText(this, text, Toast.LENGTH_LONG).show()); }
    public final class FilesBridge {
        @JavascriptInterface public void exportBackup(String json, String fileName) {
            if (json.length() > 8_000_000) { toast("Backup exceeds 8 MB."); return; }
            runOnUiThread(() -> {
                pendingExport = json;
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT).setType("application/json").addCategory(Intent.CATEGORY_OPENABLE).putExtra(Intent.EXTRA_TITLE, fileName != null && fileName.matches("[A-Za-z0-9_.-]{1,100}") ? fileName : "AE-Prepware-backup.json");
                startActivityForResult(intent, 20);
            });
        }
        @JavascriptInterface public void importFile() {
            runOnUiThread(() -> startActivityForResult(new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("application/json").addCategory(Intent.CATEGORY_OPENABLE),21));
        }
    }
    @Override protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); out.putString("pendingExport",pendingExport); }
    @Override protected void onRestoreInstanceState(Bundle in) { super.onRestoreInstanceState(in); pendingExport=in.getString("pendingExport"); }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request,result,data);
        if (result != RESULT_OK || data == null || data.getData() == null) return;
        try {
            if (request==20 && pendingExport!=null) {
                try (OutputStream out=getContentResolver().openOutputStream(data.getData(),"wt")) { if(out==null) throw new IOException(); out.write(pendingExport.getBytes(StandardCharsets.UTF_8)); }
                pendingExport=null; toast("Backup saved.");
            } else if (request==21) {
                try (InputStream in=getContentResolver().openInputStream(data.getData()); ByteArrayOutputStream out=new ByteArrayOutputStream()) {
                    if(in==null) throw new IOException();
                    byte[] buffer=new byte[4096]; int n;
                    while((n=in.read(buffer))!=-1) { out.write(buffer,0,n); if(out.size()>8_000_000) throw new IOException("File exceeds 8 MB"); }
                    web.evaluateJavascript("window.receiveImport("+JSONObject.quote(out.toString("UTF-8"))+")",null);
                }
            }
        } catch (IOException ex) { toast("File could not be read or saved. Your current progress is unchanged."); }
    }
    @Override public void onBackPressed() { web.evaluateJavascript("window.handleBack()",null); }
    @Override protected void onDestroy() { web.removeJavascriptInterface("AndroidFiles"); web.destroy(); super.onDestroy(); }
}
