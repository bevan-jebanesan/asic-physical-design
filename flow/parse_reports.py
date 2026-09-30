import re, os, sys

clk_per=sys.argv[1]
init_util=sys.argv[2]
max_layer=sys.argv[3]
max_trans=sys.argv[4]
hold_uncert=sys.argv[5]

results=open('results.csv','a')

results.write(open('dcrm/synth.begin').readlines()[0].strip()+',')
results.write(open('dcrm/synth').readlines()[0].strip()+',')
results.write(open('icc2rm/init_design.begin').readlines()[0].strip()+',')
results.write(open('icc2rm/init_design').readlines()[0].strip()+',')
results.write(open('icc2rm/place_opt.begin').readlines()[0].strip()+',')
results.write(open('icc2rm/place_opt').readlines()[0].strip()+',')
results.write(open('icc2rm/clock_opt_cts.begin').readlines()[0].strip()+',')
results.write(open('icc2rm/clock_opt_cts').readlines()[0].strip()+',')
results.write(open('icc2rm/clock_opt_opto.begin').readlines()[0].strip()+',')
results.write(open('icc2rm/clock_opt_opto').readlines()[0].strip()+',')
results.write(open('icc2rm/route_auto.begin').readlines()[0].strip()+',')
results.write(open('icc2rm/route_auto').readlines()[0].strip()+',')
results.write(open('icc2rm/route_opt.begin').readlines()[0].strip()+',')
results.write(open('icc2rm/route_opt').readlines()[0].strip()+',')
results.write(open('icc2rm/hostname').readlines()[0].strip()+',')
results.write(open('icc2rm/loadavg').readlines()[0].split()[2]+',')
results.write(clk_per+',')
results.write(init_util+',')
results.write(max_layer+',')
results.write(max_trans+',')
results.write(hold_uncert+',')

scenario=None
group=None
whs=None
f=open('icc2rm/rpts_icc2/route_opt.report_timing.min')
for line in f:
    m=re.search(r"^\s*Scenario:\s+(\S+)",line)
    if m:
        scenario=m.group(1)
        continue
    m=re.search(r"^\s*Path Group:\s+(\S+)",line)
    if m:
        group=m.group(1)
        continue
    m=re.search(r'^\s*slack\s+\([A-Z]+\)\s+([-+0-9\.]+)',line)
    if m:
        if scenario=='mode_norm.fast.RCmin_bc' and group=='clk':
            whs=m.group(1)
            break
f.close()
results.write(whs+',')

scenario=None
group=None
crit_path_len=None
tnhs=None
nhve=None
ntv=None
f=open('icc2rm/rpts_icc2/route_opt.report_qor')
for line in f:
    m=re.search(r"^Scenario\s+'(\S+)'",line)
    if m:
        scenario=m.group(1)
        continue
    m=re.search(r"^Timing Path Group\s+'(\S+)'",line)
    if m:
        group=m.group(1)
        continue
    m=re.search(r"^Critical Path Length:\s+([0-9\.\-]+)",line)
    if m:
        if scenario=='mode_norm.slow.RCmax' and group=='clk':
            crit_path_len=m.group(1)
        continue
    m=re.search(r"^Total Hold Violation:\s+([0-9\.\-]+)",line)
    if m:
        if scenario=='mode_norm.fast.RCmin_bc' and group=='clk':
            tnhs=m.group(1)
        continue
    m=re.search(r"^No. of Hold Violations:\s+([0-9]+)",line)
    if m:
        if scenario=='mode_norm.fast.RCmin_bc' and group=='clk':
            nhve=m.group(1)
        continue
    m=re.search(r'Max Trans Violations:\s+(\d+)',line)
    if m:
        ntv=m.group(1)
        break
f.close()

results.write(tnhs+',')
results.write(nhve+',')
results.write(ntv+',')
results.write(crit_path_len+',')

mode=None
max_trans=None
f=open('icc2rm/rpts_icc2/route_opt.report_clock_timing')
for line in f:
    m=re.search(r'Mode: (\S+)',line)
    if m:
        mode=m.group(1)
    m=re.search(r'Maximum active transition',line)
    if m:
        line=f.readline()
        m=re.search(r'^\s*\S+\s+([0-9\.]+)',line)
        if m:
            if mode=='mode_norm.fast.RCmin_bc':
                max_trans=m.group(1)
f.close()
results.write(max_trans+',')

util=None
cell_area=None
f=open('icc2rm/rpts_icc2/route_opt.report_utilization')
for line in f:
    m=re.search(r'^Utilization Ratio:\s+([0-9\.]+)',line)
    if m:
        util=m.group(1)
        continue
    m=re.search(r'^Total Area of cells:\s+([0-9\.]+)',line)
    if m:
        cell_area=m.group(1)
        break
f.close()
results.write(cell_area+',')
results.write(util+',')

viol=None
wire_len=None
f=open('icc2rm/rpts_icc2/route_opt.check_routes')
for line in f:
    m=re.search(r'TOTAL VIOLATIONS =\s+(\d+)',line)
    if m:
        viol=m.group(1)
        continue
    m=re.search(r'Total Routed Wire Length =\s+(\d+)',line)
    if m:
        wire_len=m.group(1)
        break
f.close()
results.write(viol+',')
results.write(wire_len+',')

try:
    A = float(cell_area)
    D = float(crit_path_len)
    opt_metric = (A**3) * D
    results.write(f'{opt_metric:.4f},') 
except (ValueError, TypeError):
    results.write('N/A,')

ver1=None
with open('dcrm/dc.log') as f:
    for line in f:
        m=re.search(r'Version\s+([^\s].*?)\s+for linux64',line)
        if m:
            ver1=m.group(1).strip()
            break
results.write((ver1 if ver1 else 'N/A')+',')

ver2=None
with open('icc2rm/logs_icc2/route_opt.log') as f:
    for line in f:
        m=re.search(r'Version\s+([^\s].*?)\s+for linux64',line)
        if m:
            ver2=m.group(1).strip()
            break
results.write((ver2 if ver2 else 'N/A')+',')

metal_wl = {'metal1': 'N/A','metal2':'N/A','metal3':'N/A','metal4':'N/A','metal5':'N/A'}
with open('icc2rm/rpts_icc2/route_opt.check_routes') as f:
    for line in f:
        m = re.search(r'Layer\s+(Metal[1-5])\s*:\s*([\d\.]+)', line, re.IGNORECASE)
        if m:
            metal_wl[m.group(1).lower()] = m.group(2)
for m in ['metal1','metal2','metal3','metal4','metal5']:
    results.write(metal_wl[m]+',')

f = open('icc2rm/rpts_icc2/route_opt.report_power')
int_pwr = None
sw_pwr = None
leak_pwr = None
scenario = None
for line in f:
    m = re.search(r'^\s*Scenario:\s+(\S+)', line)
    if m:
        scenario = m.group(1)
        continue
    if scenario == 'mode_norm.fast.RCmin':
        m_int = re.search(r'Cell Internal Power\s*=\s*([\deE\+\-\.]+)', line)
        if m_int:
            int_pwr = m_int.group(1)
        m_sw = re.search(r'Net Switching Power\s*=\s*([\deE\+\-\.]+)', line)
        if m_sw:
            sw_pwr = m_sw.group(1)
        m_leak = re.search(r'Cell Leakage Power\s*=\s*([\deE\+\-\.]+)', line)
        if m_leak:
            leak_pwr = m_leak.group(1)
f.close()
results.write((int_pwr if int_pwr else '0')+',')
results.write((sw_pwr if sw_pwr else '0')+',')
results.write((leak_pwr if leak_pwr else '0')+'\n')
results.close()
