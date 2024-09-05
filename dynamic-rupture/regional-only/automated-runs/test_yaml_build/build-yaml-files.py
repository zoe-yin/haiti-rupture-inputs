import yaml
import os
import shutil
import glob

import yaml
def create_Haiti_sig_zz_yaml(Pf_value,writedir):
    yaml_content = f"""!LuaMap
returns: [sig_zz]
function: |
  function f (x)
    return {{
      sig_zz = math.max(-52000000, 2670.0*{Pf_value}*9.8*math.min(-200.0,x["z"]))
    }}
  end
"""

    filename = writedir + "Haiti_sig_zz.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")


def create_Haiti_initial_stress_yaml(SH_max_value, s2ratio_value, mu_s_value, mu_d_value, writedir):
    yaml_content = f"""!EvalModel  # this indicates that we want to evaluate the parameters below before calculating the sxx, sxy, syy components
parameters: [Omega, sig_zz, b_xx, b_yy, b_zz, b_xy, b_yz, b_xz, bc_xx, bc_yy, bc_zz, bc_xy, bc_yz, bc_xz]
model: !Switch
  [Omega]: !LuaMap  # Depth dependent stress accumulation 
        returns: [Omega]
        function: |
         function f (x)
           zStressDecreaseStart = -25000.;
           zStressDecreaseStop = -28000.;
           zStressDecreaseWidth = zStressDecreaseStart - zStressDecreaseStop;
           if (x["z"] >= zStressDecreaseStart) then
              Omega = 1.0
           elseif (x["z"] >= zStressDecreaseStop) then
              a = 1.0-(x["z"]-zStressDecreaseStop)/zStressDecreaseWidth;
              Sx = (3.0*a*a-2.0*a*a*a);
              Omega = 1.0-0.99*Sx;
           else
              Omega = 0.01;
           end
           return {{
             Omega = Omega
           }}
           end
  [b_xx, b_yy, b_zz, b_xy, b_yz, b_xz]: !EvalModel
    parameters: [sig_zz,S, SH_max]
    model: !Switch  
      [sig_zz]: !Include Haiti_sig_zz.yaml
      [SH_max]: !Any 
          components:
            - !GroupFilter
              groups: [65,66,67,68,69,70]  
              components: !ConstantMap
                map:
                    SH_max: {SH_max_value}  # Update SH_max with the value that makes sense for Haiti
      [S]: !Any
          components:
            - !GroupFilter
              groups: [65, 66]  # Change the fault tags here !
              components: !LuaMap
                returns: [S]
                function: |
                 function f (x)
                  R = 1.0
                  return {{
                    S = (1.0/R-1.0)
                  }}
                  end
            - !GroupFilter
              groups: [67,68,69,70]  # Change the fault tags here !
              components: !LuaMap
                returns: [S]
                function: |
                 function f (x)
                  R = 1.0
                  return {{
                    S = (1.0/R-1.0)
                  }}
                  end                 
    components: !AndersonianStress
      constants:
        mu_d: {mu_d_value}
        mu_s: {mu_s_value}
        cohesion:  0.0
        s2ratio: {s2ratio_value}  # pure strike-slip faulting (no transtensional or transpressional regime)
        S_v: 3  # Andersonian stress regime (2 = strike slip, 3 = thrust)
  [sig_zz]: !Include Haiti_sig_zz.yaml
  [bc_xx, bc_yy, bc_zz,bc_xy, bc_yz, bc_xz]: !Include Haiti_stress_change.yaml  
components: !LuaMap
  returns: [s_xx, s_yy, s_zz, s_xy, s_yz, s_xz]
  function: |
     function f (x)
      return {{
        s_xx = x["Omega"] * (x["b_xx"] - x["bc_xx"]) + (1.0-x["Omega"]) * x["sig_zz"],
        s_yy = x["Omega"] * (x["b_yy"] - x["bc_yy"]) + (1.0-x["Omega"]) * x["sig_zz"],
        s_zz = x["Omega"] * (x["b_zz"] - x["bc_zz"]) + (1.0-x["Omega"]) * x["sig_zz"],
        s_xy = x["Omega"] * (x["b_xy"] - x["bc_xy"]),
        s_yz = x["Omega"] * (x["b_yz"] - x["bc_yz"]),
        s_xz = x["Omega"] * (x["b_xz"] - x["bc_xz"])
      }}
      end
"""

    filename = writedir + "Haiti_initial_stress.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")


def create_Haiti_alpha_yaml(alpha_value, writedir):
    yaml_content = f"""!Any    
components:
  - !GroupFilter
      groups: [65,66]  # Change fault tag
      components: !ConstantMap
        map:
          alpha: {alpha_value}  
  - !GroupFilter
      groups: [67,68,69,70]  # Change fault tag
      components: !ConstantMap
        map:
          alpha: {alpha_value}                   
"""

    filename = writedir + "Haiti_alpha.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")

def create_Haiti_forced_rupture_time_yaml(r_crita_value, writedir):
    yaml_content = f"""!LuaMap
returns: [forced_rupture_time]
function: |
    function f (x)
      xha = {{658404, 2036560, -10049}} 
      r_crita = {r_crita_value}
      ra = math.sqrt((x["x"]-xha[1])^2 + (x["y"]-xha[2])^2 + (x["z"]-xha[3])^2 )
      Vs = 3464.0
      if (ra <= r_crita) then
        forced_rupture_time =  ra/(0.7*Vs)+(0.081*r_crita/(0.7*Vs))*(1.0/(1.0-(ra/r_crita)^2)-1.0)
      else
        forced_rupture_time = 1000000000.0
      end
      return {{
        forced_rupture_time = forced_rupture_time
      }}
    end
# Change xha and r_crita
# xha: coordinates of nucleation point
# r_crita: size of the nucleation patch 
"""

    filename = writedir + "Haiti_forced_rupture_time.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")


def create_Haiti_fault_yaml(mu_s_value, mu_d_value, d_c_value, writedir):
    yaml_content = f"""!Switch
[mu_s, mu_d, Tnuc_n, Tnuc_s, Tnuc_d]: !ConstantMap
  map:
    mu_s: {mu_s_value}
    mu_d: {mu_d_value}
    Tnuc_n: 0
    Tnuc_s: 0
    Tnuc_d: 0

[d_c]: !Any
  components:
    - !ConstantMap
        map:
          d_c: {d_c_value}
[forced_rupture_time]: !Include Haiti_forced_rupture_time.yaml
[cohesion]: !LuaMap  # Check and update for your case
  returns: [cohesion]
  function: |
   function f (x)
    z = x["z"]
    cohesion = -0.5e6
    zIncreasingCohesion = 6000.0
    if (z >= -zIncreasingCohesion) then
      cohesion = cohesion - 2.0e6 * (z+zIncreasingCohesion)/zIncreasingCohesion;
    end
    return {{
      cohesion = cohesion
    }}
    end
[s_xx, s_yy, s_zz, s_xy, s_yz, s_xz]: !Include Haiti_initial_stress.yaml
"""

    filename = writedir + "Haiti_fault.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")


def create_Haiti_stress_change_kinematic_model_yaml(asagi_file, writedir):
    yaml_content = f"""!EvalModel
    parameters: [c_xx, c_yy, c_zz, c_xy, c_yz, c_xz]
    model: !Switch
      [c_xx, c_yy, c_zz, c_xy, c_yz, c_xz]: !Any
         components: !Any
           - !ASAGI
               file: {asagi_file} # Update path 
               parameters: [c_xx, c_yy, c_zz, c_xy, c_yz, c_xz]
               var: data
               interpolation: linear   
           - !ConstantMap
             map:
               c_xx: 0.0
               c_yy: 0.0
               c_zz: 0.0
               c_xy: 0.0
               c_yz: 0.0
               c_xz: 0.0
"""

    filename = writedir + "Haiti_stress_change_kinematic_model.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")


# def create_Haiti_stress_change_yaml(asagi_file):
#     shutil.copy('/dss/dsshome1/01/di35poq/haiti-rupture-inputs/dynamic-rupture/regional-only/automated-runs/template_yamls/Haiti_stress_change.yaml', '.')


def create_Haiti_stress_change_yaml(writedir):
    yaml_content = """!EvalModel
parameters: [c_xx, c_yy, c_zz, c_xy, c_yz, c_xz, alpha]
model: !Switch
  [c_xx, c_yy, c_zz, c_xy, c_yz, c_xz]: !Include Haiti_stress_change_kinematic_model.yaml
  [alpha]: !Include Haiti_alpha.yaml
components: 
!LuaMap
  returns: [bc_xx, bc_yy, bc_zz, bc_xy, bc_yz, bc_xz]
  function: |
     function f (x)
      return {
        bc_xx = x["c_xx"] * x["alpha"],
        bc_yy = x["c_yy"] * x["alpha"],
        bc_zz = x["c_zz"] * x["alpha"],
        bc_xy = x["c_xy"] * x["alpha"],
        bc_yz = x["c_yz"] * x["alpha"],
        bc_xz = x["c_xz"] * x["alpha"]
      }
      end
"""

    filename = writedir + "Haiti_stress_change.yaml"
    with open(filename, 'w') as file:
        file.write(yaml_content)
    print(f"YAML file created: {filename}")

def create_parameters_par(EndTime_value, writedir):
    par_content = f"""&equations
!yaml file defining spatial dependance of material properties
MaterialFileName = '/dss/dsshome1/01/di35poq/haiti-rupture-inputs/material-properties/haiti_material_properties_douilly-2021.yaml'
/

&IniCondition
/

&Boundaries
BC_fs = 1                                      ! enable free surface boundaries
BC_dr = 1                                      ! enable fault boundaries
BC_of = 1                                      ! enable absorbing boundaries
/

&DynamicRupture
FL = 16                                      ! Friction law, 33 is Yoffe, 34 is Gaussian
!0: none, 16:LSW, 103: RS with strong velocity weakening
!yaml file defining spatial dependance of fault properties
ModelFileName = 'Haiti_fault.yaml'

!reference vector for defining strike and dip direction ! @todo: need to understand/check this
refPointMethod = 1
XRef = 0.0 
YRef = -1.0
ZRef = 0.0

!see: https://seissol.readthedocs.io/en/latest/fault-output.html
OutputPointType = 4                            ! Type (0: no output, 3: ascii file, 4: paraview file, 5: 3+4)
SlipRateOutputType=0        ! 0: (smoother) slip rate output evaluated from the difference between the velocity on both side of the fault, two different ways to calculate the slip rate
                            ! 1: slip rate output evaluated from the fault tractions and the failure criterion (less smooth but usually more accurate where the rupture front is well developped)
/

!see: https://seissol.readthedocs.io/en/latest/fault-output.html
! parameterize paraview file output
&Elementwise
printIntervalCriterion = 2                     ! 1=iteration, 2=time
printtimeinterval_sec = 0.5                   ! Time interval at which output will be written
OutputMask = 1 1 0 1 1 1 1 1 1 1 0             ! turn on and off fault outputs, see fault-output page, linked above, @todo: would be good to review this and the next two lines
refinement_strategy = 2                         ! refinement_strategy = 2 divides each triangle into 4 triangles.
refinement = 0                                  ! refinement = 1 subdivides each triangle into 3 or 4 subtriangles, depending on the refinement_strategy. A higher refinement value will further subdivide each subtriangle.
/

&SourceType
/

&SpongeLayer
/
            
&MeshNml
MeshFile = '/dss/dsshome1/01/di35poq/mesh/mesh_v07/Haiti_v07_lowres'
meshgenerator = 'PUML'                         ! Name of meshgenerator (Gambit3D-fast, Netcdf or PUML)
/

&Discretization
CFL = 0.5                                      ! CFL number (<=1.0)
FixTimeStep = 5                                ! Manualy chosen minimum time
ClusteredLTS = 2                               ! 1 for Global time stepping, 2,3,5,... Local time stepping (advised value 2)
!ClusteredLTS defines the multi-rate for the time steps of the clusters 2 for Local time stepping
/

&Output
FaultOutputFlag = 1                            ! DR output (add this line only if DR is active)
OutputFile='/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-rupture-outputs/regional-only/jobid_3857104/output'
Format = 10                                     ! Format (10= no output, 6=hdf5 output)
!             |stress     |vel  
iOutputMask = 0 0 0 0 0 0 1 1 1
!                 |strain     |eta
!iPlasticityMask = 0 0 0 0 0 0 1
TimeInterval =  10.                           ! Index of printed info at time
refinement = 0
EnergyOutput = 1                  ! Computation of energy, written in csv file
EnergyTerminalOutput = 1          ! Write energy to standard output
EnergyOutputInterval = 0.5

! Free surface output
SurfaceOutput = 1
SurfaceOutputRefinement = 0
SurfaceOutputInterval = 1

printIntervalCriterion = 2          ! Criterion for index of printed info: 1=timesteps,2=time,3=timesteps+time

pickdt = 0.05                       ! Pickpoint Sampling
pickDtType = 1                       ! Pickpoint Type
RFileName = ''       ! Record Points in extra file @todo: Not sure if we need this?
ReceiverOutputInterval = 10.0

!xdmfWriterBackend = 'posix' ! (optional) The backend used in fault, wavefield,
! and free-surface output. The HDF5 backend is only supported when SeisSol is compiled with
! HDF5 support.
!RFileName = 'test.dat'          ! Record Points in extra file @todo: what does this file do? 
/

&AbortCriteria
EndTime = {EndTime_value}
/

&Analysis
/
p
&Debugging
/

"""

    filename = writedir + "parameters.par"
    with open(filename, 'w') as file:
        file.write(par_content)
    print(f"Parameter file created: {filename}")


def copy_slurm_file(writedir): 
  if os.path.exists('run-supermuc-slurm.sh'):
    os.remove('run-supermuc-slurm.sh')
  shutil.copy2('/dss/dsshome1/01/di35poq/haiti-rupture-inputs/dynamic-rupture/regional-only/automated-runs/template_yamls/run-supermuc-slurm.sh', writedir + 'run-supermuc-slurm.sh')

def generate_all_input_files(writedir,alpha_value, mu_s_value, mu_d_value, d_c_value, r_crita_value, SH_max_value, s2ratio_value,Pf_value, asagi_file, EndTime_value): 
  # Generate the YAML file
  # writedir = '/dss/dsshome1/01/di35poq/haiti-rupture-inputs/dynamic-rupture/regional-only/automated-runs/yaml_build_test/job_SHmax_40.0_nu_0.0/'
  create_Haiti_alpha_yaml(alpha_value,writedir=writedir)
  create_Haiti_fault_yaml(mu_s_value, mu_d_value, d_c_value,writedir=writedir)
  create_Haiti_forced_rupture_time_yaml(r_crita_value,writedir=writedir)
  create_Haiti_initial_stress_yaml(SH_max_value, s2ratio_value, mu_s_value, mu_d_value,writedir=writedir)
  create_Haiti_sig_zz_yaml(Pf_value,writedir=writedir)
  create_Haiti_stress_change_kinematic_model_yaml(asagi_file,writedir=writedir)
  create_Haiti_stress_change_yaml(writedir=writedir)

  # Create parameter file
  create_parameters_par(EndTime_value=EndTime_value,writedir=writedir)
  # Create a slurm file: 
  copy_slurm_file(writedir=writedir)


# writedir= '/dss/dsshome1/01/di35poq/haiti-rupture-inputs/dynamic-rupture/regional-only/automated-runs/yaml_build_test/job_SHmax_40.0_nu_0.0/'
alpha_value=0.5
mu_s_value=0.3
mu_d_value=0.5
d_c_value=0.1
r_crita_value=6000
# SH_max_value=60
# s2ratio_value=0.1
Pf_value=0.34
asagi_file='/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-relaxation-outputs/jobid_3437321/gridded_asagi_taper_200-1500_0.nc'
EndTime_value=1.0

# generate_all_input_files(writedir,alpha_value, mu_s_value, mu_d_value, d_c_value, r_crita_value, SH_max_value, s2ratio_value,Pf_value, asagi_file, EndTime_value)

# Example of creating multiple YAML files with different parameter values
s2ratio_values = [0.0, 0.1]  # Range of Omega values
SH_max_values = [40.0, 50.0]  # Range of SH_max values

for s2ratio_value in s2ratio_values:
    for SH_max_value in SH_max_values:
      # Create a job directory for each value combination (if doesn't already exist)
      cwd = os.getcwd()
      if not os.path.exists(f"job_SHmax_{SH_max_value}_nu_{s2ratio_value}"):
        os.mkdir(f"job_SHmax_{SH_max_value}_nu_{s2ratio_value}")
      # Define our variables for this combo of parameters
      writedir=f"{cwd}/job_SHmax_{SH_max_value}_nu_{s2ratio_value}/"
      print("writedir = " + writedir)
      print("Creating YAML files for values: " + str(SH_max_value) + " + s2ratio: " + str(s2ratio_value))
      generate_all_input_files(writedir,alpha_value, mu_s_value, mu_d_value, d_c_value, r_crita_value, SH_max_value, s2ratio_value,Pf_value, asagi_file, EndTime_value)



######################

# Example usage
# create_Haiti_forced_rupture_time_yaml(7000.0)

# writedir = '/dss/dsshome1/01/di35poq/haiti-rupture-inputs/dynamic-rupture/regional-only/automated-runs/yaml_build_test/job_SHmax_40.0_nu_0.0/'
# create_Haiti_alpha_yaml(alpha_value=0.5,writedir=writedir)
# create_Haiti_fault_yaml(mu_s_value=0.5, mu_d_value=0.35, d_c_value=0.01,writedir=writedir)
# create_Haiti_forced_rupture_time_yaml(r_crita_value=7000.0,writedir=writedir)
# create_Haiti_initial_stress_yaml(SH_max_value=40.0, s2ratio_value=0.2, mu_s_value=0.5, mu_d_value=0.35,writedir=writedir)
# create_Haiti_sig_zz_yaml(0.34,writedir=writedir)
# create_Haiti_stress_change_kinematic_model_yaml(asagi_file='/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-relaxation-outputs/jobid_3437321/gridded_asagi_taper_200-1500_0.nc',writedir=writedir)
# create_Haiti_stress_change_yaml(writedir=writedir)

# # Create parameter file
# create_parameters_par(EndTime_value=1.0,writedir=writedir)
# # Create a slurm file: 
# copy_slurm_file(writedir=writedir)

# mu_s = 0.5
# mu_d = 0.3
# asagi_filepath = '/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-relaxation-outputs/jobid_3437321/gridded_asagi_taper_200-1500_0.nc'
# r_crita = 7000.0


# create_Haiti_forced_rupture_time_yaml(r_crita)
# create_Haiti_fault_yaml(mu_s, mu_d)
# create_Haiti_stress_change_yaml()
# create_Haiti_stress_change_kinematic_model_yaml(asagi_filepath)
# create_Haiti_alpha_yaml()
# create_Haiti_sig_zz_yaml()

# # Example of creating multiple YAML files with different parameter values
# s2ratio_values = [0.0, 0.1, 0.2]  # Range of Omega values
# SH_max_values = [40.0, 50.0, 60.0]  # Range of SH_max values

# for s2ratio_value in s2ratio_values:
#     for SH_max_value in SH_max_values:
#         print("Creating YAML for SH_max: " + str(SH_max_value) + " + s2ratio: " + str(s2ratio_value))
#         create_yaml(s2ratio_value, SH_max_value)
#         # Create a job directory for each value combination (if doesn't already exist)
#         if not os.path.exists(f"job_SHmax_{SH_max_value}_nu_{s2ratio_value}"):
#           os.mkdir(f"job_SHmax_{SH_max_value}_nu_{s2ratio_value}")       
#         # Copy all yaml files to the job directory 
#         for file in glob.glob(r'*.yaml'):
#             print(file)
#             shutil.copy(file, f"job_SHmax_{SH_max_value}_nu_{s2ratio_value}")