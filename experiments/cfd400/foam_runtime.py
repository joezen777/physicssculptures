from pathlib import Path
import os
CACHE=Path.home()/'.cache/angularmomflyer/openfoam'
PROJECT=CACHE/'maintained/usr/lib/openfoam/openfoam1912'
PLATFORM=PROJECT/'platforms/linux64GccDPInt32Opt'
BIN=PLATFORM/'bin'
ENV=os.environ.copy()
ENV.update(WM_PROJECT_DIR=str(PROJECT),FOAM_ETC=str(PROJECT/'etc'),
 LD_LIBRARY_PATH=':'.join(map(str,[PLATFORM/'lib',PLATFORM/'lib/openmpi-system',PLATFORM/'lib/dummy',CACHE/'root/usr/lib/x86_64-linux-gnu'])),
 OPAL_PREFIX=str(CACHE/'root/usr'),
 OMPI_MCA_mca_base_component_path=str(CACHE/'root/usr/lib/x86_64-linux-gnu/openmpi/lib/openmpi3'))
ENV['PATH']=str(BIN)+':'+str(CACHE/'root/usr/bin')+':'+ENV['PATH']
