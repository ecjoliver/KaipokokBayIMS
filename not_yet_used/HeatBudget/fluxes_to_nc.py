'''
Save all fluxes into a net CDF file
'''


# Daily 
ds = xr.Dataset(coords={"time": T_a.time})
ds = IMS.add_to_dataset(ds, "F_netLWR",F_lw_net,attrs={"long_name":"Net longwave radiation (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_netSWR",F_sw_net,attrs={"long_name":"Net shortwave radiation (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_sens",F_sens,attrs={"long_name":"Sensible heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_lat",F_lat,attrs={"long_name":"Latent heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_c_surf",F_c_surf,attrs={"long_name":"Surface (0-10cm) conductive heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_net_surf",F_net_surf,attrs={"long_name":"Net surface heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_c_bot",F_c_daily,attrs={"long_name":"Internal conductive heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_snowmelt",F_snowmelt,attrs={"long_name":"Latent heat of snowmelt (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_icemelt",F_icemelt,attrs={"long_name":"Latent heat of surface ice melt (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_ocean",F_w_daily_quad,attrs={"long_name":"Ice-ocean heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_g",F_l_daily,attrs={"long_name":"Latent heat of ice growth at the bottom (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_net_bot",F_bot,attrs={"long_name":"Net bottom heat flux (W/m^2)"})

ds.to_netcdf('HeatBudget/Fluxes_daily.nc')

# 6-hourly 
F_sw_6H = ds_weather['RsNet_Avg'].resample(time='6H').mean('time') # net SW should be negative
F_lw_6H = ds_weather['RlNet_Avg'].resample(time='6H').mean('time') # net SW should be negative
U_wd_10m_6H = U_wd_10m_hourly.resample(time='6H').mean('time')
T_s_6H = (((LWout - (1-epsilon)*LWin)/(epsilon*sigma))**0.25 - 273.15).resample(time='6H').mean('time')
T_a_6H = ds_weather['AirT_C_Avg'].resample(time='6H').mean('time') # Air temperature
RH_6H = ds_weather['Humidity'].resample(time='6H').mean('time')
P_6H = ds_weather.BP_mbar_Avg.resample(time='6H').mean('time') # mbar


F_sens_6H,___ = IMS.sensible_heat_flux(U_wd_10m_6H,T_s_6H,T_a_6H,0,0,0)
F_lat_6H = IMS.latent_heat_flux(U_wd_10m_6H, RH_6H, P_6H, T_s_6H, T_a_6H)

Fw_6H = Fw_quad_detided.resample(time='6H').mean('time')
da_temp_6H = da_temp.resample(time='6H').mean('time')
snow_air_6H = snow_air.interp(time=da_temp_6H.time,method='linear')
temp_ice_snow = da_temp_6H.where(
    (da_temp_6H.z < snow_air_6H) &  
    (da_temp_6H.z > H_bottom.resample(time='6H').mean('time'))
    )
dT_dz_full = -temp_ice_snow.differentiate('z') 
F_c_full = -k_s * (dT_dz_full) # Assume most of it is snow
surf_layer_lower = snow_air_6H-z1 # Bottom of the layer is 20 cm below the snow surface, doesn't matter if it's snow or ice
surf_layer_upper = snow_air_6H
k_s_i = xr.zeros_like(T_a_6H)*np.nan
k_s_i = k_s_i.where(H_snow.interp(time=da_temp_6H.time,method='linear') < 0.05, k_s).fillna(k_i)
# Fc through the surface layer
dT_dz_surf = dT_dz_full.where(
    (dT_dz_full.z < surf_layer_upper) & 
    (dT_dz_full.z > surf_layer_lower), 
    other=np.nan
    )
F_c_surf_2d = -k_s_i*dT_dz_surf
F_c_surf_6H = F_c_surf_2d.mean('z')

F_c_6H = F_c.resample(time='6H').mean('time')

# Sum of surface fluxes
F_surf = F_lw_6H + F_sw_6H + F_sens_6H + F_lat_6H

# Net energy flux at the surface
F_net_surf_6H = F_surf - F_c_surf_6H

F_l_6H = F_l.resample(time='6H').mean()
F_bot_6H = F_l_6H - F_c_6H - Fw_6H


ds = xr.Dataset(coords={"time": F_sw_6H.time})
ds = IMS.add_to_dataset(ds, "F_netLWR",F_lw_6H,attrs={"long_name":"Net longwave radiation (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_netSWR",F_sw_6H,attrs={"long_name":"Net shortwave radiation (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_sens",F_sens_6H,attrs={"long_name":"Sensible heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_lat",F_lat_6H,attrs={"long_name":"Latent heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_c_surf",F_c_surf_6H,attrs={"long_name":"Surface (0-10cm) conductive heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_net_surf",F_net_surf_6H,attrs={"long_name":"Net surface heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_c_bot",F_c_6H,attrs={"long_name":"Internal conductive heat flux (W/m^2)"})
# ds = IMS.add_to_dataset(ds, "F_icemelt",F_snowmelt,attrs={"long_name":"Latent heat of surface ice melt (W/m^2)"})
# ds = IMS.add_to_dataset(ds, "F_snowmelt",F_snowmelt,attrs={"long_name":"Latent heat of snowmelt (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_ocean",Fw_6H,attrs={"long_name":"Ice-ocean heat flux (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_g",F_l_6H,attrs={"long_name":"Latent heat of ice growth at the bottom (W/m^2)"})
ds = IMS.add_to_dataset(ds, "F_net_bot",F_bot_6H,attrs={"long_name":"Net bottom heat flux (W/m^2)"})



ds.to_netcdf('HeatBudget/Fluxes_6H.nc')





