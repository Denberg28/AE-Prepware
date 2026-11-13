"""Append original, source-checked feedback exercises without changing old keys.

Run with --bank INPUT --output OUTPUT. No recalled exam wording is used.
The separate test solves the printed givens independently of these generators.
"""
import argparse
import copy
import json
import math
from pathlib import Path

SOURCES = {
    'feedback-nav': {
        'title': 'FAA Pilot’s Handbook of Aeronautical Knowledge, Chapter 16',
        'url': 'https://www.faa.gov/sites/faa.gov/files/18_phak_ch16.pdf',
        'locator': 'Navigation: Magnetic Variation; Compass Deviation; Wind Triangle; ADF, figures 16-37 and 16-38. Original exercises, not FAA or PRC exam items.'},
    'feedback-nozzle': {
        'title': 'NASA Glenn: Compressible Area Ratio',
        'url': 'https://www.grc.nasa.gov/www/BGH/astar.html',
        'locator': 'Calorically perfect gas mass flow, sonic throat and area–Mach equations. Original exercises; SI units and ideal isentropic assumptions stated in each stem.'},
}

def exercises():
    rows=[]
    def add(code,topic,prompt,value,unit,explanation,source,wrong=None):
        fmt=lambda x: f'{x:.3f}'.rstrip('0').rstrip('.')
        values=[value,*(wrong if wrong is not None else [value/2,value*2,value*1.5])]
        choices=[f'{fmt(x)}{unit}' for x in values]
        assert len(set(choices))==4
        rows.append(dict(id=code,subject='aero',origin='AI',topic=topic,prompt=prompt,
            choices=choices,answer=0,explanation=explanation,source=source,
            review='source-checked',reviewer='AE Prepware author: formula, assumptions and arithmetic self-review; independent faculty review pending',reviewedAt='2026-11-14'))
    for i,(heading,relative) in enumerate([(300,270),(350,25),(75,310)],1):
        value=(heading+relative)%360
        add(f'FB-B{i:02}','Bearing computation',f'Magnetic heading is {heading}°. A fixed-card ADF indicates relative bearing {relative}° clockwise from the nose. Find the magnetic bearing TO the station (000°–359°).',value,'°',f'MB TO = (MH + RB) modulo 360 = ({heading} + {relative}) modulo 360 = {value}°. Heading and bearing use magnetic north; relative bearing uses the nose.','feedback-nav',[(value+180)%360,relative,heading])
    for i,to in enumerate([70,245,355],4):
        value=(to+180)%360
        add(f'FB-B{i:02}','Bearing computation',f'The magnetic bearing TO an NDB is {to}°. What is the reciprocal magnetic bearing FROM the station (000°–359°)?',value,'°',f'Bearing FROM = (bearing TO + 180) modulo 360 = ({to} + 180) modulo 360 = {value}°. TO and FROM are reciprocal directions.','feedback-nav',[to,(to+90)%360,(to+270)%360])
    for i,(true,var,dev) in enumerate([(95,7,2),(350,-12,3),(8,11,-4)],1):
        value=(true-var-dev)%360
        variation=f'{abs(var)}° '+('E' if var>0 else 'W');deviation=f'{abs(dev)}° '+('E' if dev>0 else 'W')
        add(f'FB-H{i:02}','Heading computation',f'True heading is {true}°, variation {variation}, and deviation {deviation}. Convert TRUE to MAGNETIC to COMPASS heading. Find compass heading (000°–359°).',value,'°',f'From true to magnetic subtract east variation, add west. From magnetic to compass subtract east deviation, add west. CH = ({true} − ({var}) − ({dev})) modulo 360 = {value}°. Wind correction is already included in the given heading.','feedback-nav',[(true+var+dev)%360,(true-var)%360,(value+180)%360])
    for i,(course,tas,cross) in enumerate([(90,100,20),(0,120,30),(270,150,15)],4):
        value=(course-math.degrees(math.asin(cross/tas)))%360
        add(f'FB-H{i:02}','Heading computation',f'Desired TRUE course is {course}°, TAS {tas} kt, with wind {cross} kt blowing directly FROM the LEFT of that course (no along-course component). Find true heading to hold the course, to 0.001° (000°–359.999°).',value,'°',f'Crab left into wind. Wind correction magnitude = asin({cross}/{tas}). TH = ({course} − asin({cross}/{tas}) in degrees) modulo 360 = {value:.3f}°. All directions are true; do not add variation.','feedback-nav',[(course+math.degrees(math.asin(cross/tas)))%360,course,(value+180)%360])
    for i,(mass,rho,speed) in enumerate([(6,1.2,250),(12,1.5,400)],1):
        value=mass/(rho*speed)
        add(f'FB-T{i:02}','Throat computation',f'Steady one-dimensional flow passes a nozzle throat at {mass} kg/s. LOCAL throat density is {rho} kg/m³ and LOCAL velocity {speed} m/s. Find throat area in m².',value,' m²',f'Continuity: A = mass flow/(local density × local velocity) = {mass}/({rho} × {speed}) = {value:.3f} m². The given local values avoid confusing total with static conditions; sonic flow is not assumed.','feedback-nozzle')
    for i,(mass,p0,t0) in enumerate([(10,500,300),(8,400,320)],3):
        gamma=1.4;gas=287
        flux=p0*1000/math.sqrt(t0)*math.sqrt(gamma/gas)*(2/(gamma+1))**((gamma+1)/(2*(gamma-1)))
        value=mass/flux*10000
        add(f'FB-T{i:02}','Throat computation',f'Air (γ = 1.4, R = 287 J/(kg·K)) flows steadily through an ideal isentropic nozzle, CHOKED at its throat. TOTAL pressure is {p0} kPa, TOTAL temperature {t0} K, and mass flow {mass} kg/s. Find sonic throat area in cm², to 0.001 cm².',value,' cm²',f'At M = 1, mass flux = p0/√T0 × √(γ/R) × [2/(γ+1)]^[(γ+1)/(2(γ−1))] = {flux:.6f} kg/(m²·s). Convert {p0} kPa to {p0*1000} Pa, then A* = {mass}/{flux:.6f} m² × 10000 = {value:.3f} cm².','feedback-nozzle')
    for i,(mach,area) in enumerate([(2,0.05),(3,0.08)],5):
        ratio=(1/mach)*((2/2.4)*(1+.2*mach*mach))**3
        value=area/ratio*10000
        add(f'FB-T{i:02}','Throat computation',f'Air (γ = 1.4) flows steadily and isentropically through a nozzle, sonic at its throat. At a SUPERSONIC station M = {mach}, area A = {area} m². Find sonic throat area A* in cm², to 0.001 cm².',value,' cm²',f'A/A* = (1/M){{[2/(γ+1)][1+(γ−1)M²/2]}}^[(γ+1)/(2(γ−1))] = {ratio:.6f}. A* = {area}/{ratio:.6f} m² × 10000 = {value:.3f} cm². Area at a supersonic station exceeds sonic area.','feedback-nozzle')
    for i,(p0,t0,which) in enumerate([(600,360,'temperature'),(500,300,'pressure')],7):
        value=t0/1.2 if which=='temperature' else p0*(2/2.4)**3.5
        unit=' K' if which=='temperature' else ' kPa'
        explanation=f'T*/T0 = 2/(γ+1) = 1/1.2; T* = {t0}/1.2 = {value:.3f} K.' if which=='temperature' else f'p*/p0 = [2/(γ+1)]^[γ/(γ−1)] = (1/1.2)^3.5; p* = {p0}×(1/1.2)^3.5 = {value:.3f} kPa.'
        add(f'FB-T{i:02}','Throat computation',f'For steady ideal isentropic air flow (γ = 1.4), total pressure is {p0} kPa and total temperature {t0} K. At a CHOKED sonic throat, find STATIC throat {which}, to 0.001'+unit+'.',value,unit,explanation+' Total and static properties are different.','feedback-nozzle')
    return rows

def extend(old):
    bank=copy.deepcopy(old)
    if any(q['id'].startswith('FB-') for q in bank['questions']):raise ValueError('Feedback pack already applied')
    bank['sources'].update(SOURCES);bank['questions'].extend(exercises())
    bank.update(version=old['version']+'-feedback1',extends=old['version'])
    return bank

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bank',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.write_text(json.dumps(extend(json.loads(a.bank.read_text())),ensure_ascii=False,indent=2)+'\n')
