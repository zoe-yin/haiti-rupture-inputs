From Mathilde via Slack (June 5, 2024): 
Hi Zoe, 
Here some .yaml files to parametrize the initial stress for your simulations. They are based on what we did for the Turkish earthquakes. I put comments directly in the file to show you where you have to make changes. This parametrization combines an Andersonian stress regime with the static stress changes derived from a  static slip model. Using the !Groupfilter and changing the R ratio and the alpha parameter,  you can choose on which fault(s) you want either only the deviatoric stress due the Andersonian stress regime, or only the stress distribution from the kinematic model, or both.

`Haiti_initial_stress.yaml` is where the Andersonian stress regime is defined (change SHmax, S_v, s2ratio with the values that make sense for Haiti). There are different `!GroupFilter`, so you can apply different R values for different faults. The omega function at the beginning of the file is to progressively taper the deviatoric stresses at depth (currently they are tapered between 14 and 18 km depth --> adapt the depths to your case).  The file also calls `Haiti_stress_change.yaml` and add the stress change tensor read  from `Haiti_stress_change.yaml`  to the Andersonian stress tensor (lines 67-80)

`Haiti_stress_change.yaml` reads  and `Haiti_alpha.yaml`

`Haiti_stress_change_kinematic_model.yaml` reads the asagi file containing the stress change tensor.

`Haiti_alpha.yaml` defines a factor by which the stress change tensor read in `Haiti_stress_change_kinematic_model.yaml`  is scaled. There are also different !GroupFilter so you can choose different scaling values depending on the fault. You can for exemple put 1 for the Raimbault faults and 0 for the others.

- `Haiti_initial_stress.yaml`-> `Haiti_stress_change.yaml` -> 
    -> `Haiti_alpha.yaml`
    -> `Haiti_stress_change_kinematic_model.yaml` --> asagi file with stress change tensor
