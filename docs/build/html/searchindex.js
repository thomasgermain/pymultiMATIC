Search.setIndex({docnames:["components","index","low_level_connector","model","modes","systemmanager"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["components.rst","index.rst","low_level_connector.rst","model.rst","modes.rst","systemmanager.rst"],objects:{"pymultimatic.api":{connector:[2,0,0,"-"],defaults:[2,0,0,"-"],error:[2,0,0,"-"],payloads:[2,0,0,"-"],urls:[2,0,0,"-"]},"pymultimatic.api.connector":{ApiConnector:[2,1,1,""]},"pymultimatic.api.connector.ApiConnector":{"delete":[2,2,1,""],get:[2,2,1,""],login:[2,2,1,""],logout:[2,2,1,""],post:[2,2,1,""],put:[2,2,1,""],query:[2,2,1,""]},"pymultimatic.api.defaults":{COOKIE_FILE_NAME:[2,3,1,""],FILES_PATH:[2,3,1,""],SERIAL_NUMBER_FILE_NAME:[2,3,1,""],SMARTPHONE_ID:[2,3,1,""]},"pymultimatic.api.error":{ApiError:[2,4,1,""]},"pymultimatic.api.payloads":{holiday_mode:[2,5,1,""],hot_water_operating_mode:[2,5,1,""],hotwater_temperature_setpoint:[2,5,1,""],quickmode:[2,5,1,""],room_operating_mode:[2,5,1,""],room_quick_veto:[2,5,1,""],room_temperature_setpoint:[2,5,1,""],zone_operating_mode:[2,5,1,""],zone_quick_veto:[2,5,1,""],zone_temperature_setback:[2,5,1,""],zone_temperature_setpoint:[2,5,1,""]},"pymultimatic.api.urls":{authenticate:[2,5,1,""],circulation:[2,5,1,""],circulation_configuration:[2,5,1,""],circulation_timeprogram:[2,5,1,""],delete_repeater:[2,5,1,""],dhw:[2,5,1,""],emf_report:[2,5,1,""],emf_report_device:[2,5,1,""],facilities_default_settings:[2,5,1,""],facilities_details:[2,5,1,""],facilities_installer_info:[2,5,1,""],facilities_list:[2,5,1,""],facilities_settings:[2,5,1,""],facilities_status:[2,5,1,""],hot_water:[2,5,1,""],hot_water_configuration:[2,5,1,""],hot_water_operating_mode:[2,5,1,""],hot_water_temperature_setpoint:[2,5,1,""],hot_water_timeprogram:[2,5,1,""],hvac:[2,5,1,""],hvac_update:[2,5,1,""],live_report:[2,5,1,""],live_report_device:[2,5,1,""],logout:[2,5,1,""],new_token:[2,5,1,""],photovoltaics:[2,5,1,""],rbr_installation_status:[2,5,1,""],rbr_underfloor_heating_status:[2,5,1,""],repeater_name:[2,5,1,""],repeaters:[2,5,1,""],room:[2,5,1,""],room_child_lock:[2,5,1,""],room_configuration:[2,5,1,""],room_device_name:[2,5,1,""],room_name:[2,5,1,""],room_operating_mode:[2,5,1,""],room_quick_veto:[2,5,1,""],room_temperature_setpoint:[2,5,1,""],room_timeprogram:[2,5,1,""],rooms:[2,5,1,""],set_ventilation_day_level:[2,5,1,""],set_ventilation_night_level:[2,5,1,""],set_ventilation_operating_mode:[2,5,1,""],system:[2,5,1,""],system_configuration:[2,5,1,""],system_datetime:[2,5,1,""],system_holiday_mode:[2,5,1,""],system_parameters:[2,5,1,""],system_quickmode:[2,5,1,""],system_status:[2,5,1,""],ventilation:[2,5,1,""],ventilation_configuration:[2,5,1,""],ventilation_timeprogram:[2,5,1,""],zone:[2,5,1,""],zone_configuration:[2,5,1,""],zone_cooling_configuration:[2,5,1,""],zone_cooling_manual_setpoint_temperature:[2,5,1,""],zone_cooling_mode:[2,5,1,""],zone_cooling_setpoint_temperature:[2,5,1,""],zone_cooling_timeprogram:[2,5,1,""],zone_heating_configuration:[2,5,1,""],zone_heating_mode:[2,5,1,""],zone_heating_setback_temperature:[2,5,1,""],zone_heating_setpoint_temperature:[2,5,1,""],zone_heating_timeprogram:[2,5,1,""],zone_name:[2,5,1,""],zone_quick_veto:[2,5,1,""],zones:[2,5,1,""]},"pymultimatic.model":{component:[0,0,0,"-"],mode:[4,0,0,"-"]},"pymultimatic.model.component":{Circulation:[0,1,1,""],Component:[0,1,1,""],Device:[0,1,1,""],HotWater:[0,1,1,""],Room:[0,1,1,""],Zone:[0,1,1,""]},"pymultimatic.model.component.Circulation":{MODES:[0,6,1,""]},"pymultimatic.model.component.Component":{active_mode:[0,2,1,""]},"pymultimatic.model.component.HotWater":{MAX_TARGET_TEMP:[0,6,1,""],MIN_TARGET_TEMP:[0,6,1,""],MODES:[0,6,1,""]},"pymultimatic.model.component.Room":{MAX_TARGET_TEMP:[0,6,1,""],MIN_TARGET_TEMP:[0,6,1,""],MODES:[0,6,1,""]},"pymultimatic.model.component.Zone":{MAX_TARGET_TEMP:[0,6,1,""],MIN_TARGET_TEMP:[0,6,1,""],MODES:[0,6,1,""]},"pymultimatic.model.mode":{ActiveMode:[4,1,1,""],HolidayMode:[4,1,1,""],Mode:[4,1,1,""],OperatingMode:[4,1,1,""],OperatingModes:[4,1,1,""],QuickMode:[4,1,1,""],QuickModes:[4,1,1,""],QuickVeto:[4,1,1,""],SettingMode:[4,1,1,""],SettingModes:[4,1,1,""]},"pymultimatic.model.mode.HolidayMode":{active_mode:[4,2,1,""],is_applied:[4,2,1,""]},"pymultimatic.model.mode.OperatingModes":{AUTO:[4,6,1,""],DAY:[4,6,1,""],MANUAL:[4,6,1,""],NIGHT:[4,6,1,""],OFF:[4,6,1,""],ON:[4,6,1,""],QUICK_VETO:[4,6,1,""],get:[4,2,1,""]},"pymultimatic.model.mode.QuickModes":{HOLIDAY:[4,6,1,""],HOTWATER_BOOST:[4,6,1,""],ONE_DAY_AT_HOME:[4,6,1,""],ONE_DAY_AWAY:[4,6,1,""],PARTY:[4,6,1,""],QUICK_VETO:[4,6,1,""],SYSTEM_OFF:[4,6,1,""],VENTILATION_BOOST:[4,6,1,""],for_dhw:[4,2,1,""],for_room:[4,2,1,""],for_zone:[4,2,1,""],get:[4,2,1,""]},"pymultimatic.model.mode.SettingModes":{DAY:[4,6,1,""],NIGHT:[4,6,1,""],OFF:[4,6,1,""],ON:[4,6,1,""],get:[4,2,1,""]},"pymultimatic.model.status":{BoilerStatus:[3,1,1,""],Error:[3,1,1,""],SystemStatus:[3,1,1,""]},"pymultimatic.model.status.BoilerStatus":{is_error:[3,2,1,""]},"pymultimatic.model.status.SystemStatus":{is_online:[3,2,1,""],is_up_to_date:[3,2,1,""]},"pymultimatic.model.syncstate":{SyncState:[3,1,1,""]},"pymultimatic.model.syncstate.SyncState":{is_init:[3,2,1,""],is_outdated:[3,2,1,""],is_pending:[3,2,1,""],is_synced:[3,2,1,""]},"pymultimatic.model.system":{System:[0,1,1,""]},"pymultimatic.model.system.System":{get_active_mode_circulation:[0,2,1,""],get_active_mode_hot_water:[0,2,1,""],get_active_mode_room:[0,2,1,""],get_active_mode_zone:[0,2,1,""],set_room:[0,2,1,""],set_zone:[0,2,1,""]},"pymultimatic.model.timeprogram":{TimePeriodSetting:[3,1,1,""],TimeProgram:[3,1,1,""],TimeProgramDay:[3,1,1,""]},"pymultimatic.model.timeprogram.TimePeriodSetting":{absolute_minutes:[3,6,1,""]},"pymultimatic.model.timeprogram.TimeProgram":{get_for:[3,2,1,""]},"pymultimatic.systemmanager":{SystemManager:[5,1,1,""]},"pymultimatic.systemmanager.SystemManager":{get_circulation:[5,2,1,""],get_hot_water:[5,2,1,""],get_room:[5,2,1,""],get_system:[5,2,1,""],get_zone:[5,2,1,""],login:[5,2,1,""],logout:[5,2,1,""],remove_holiday_mode:[5,2,1,""],remove_quick_mode:[5,2,1,""],remove_room_quick_veto:[5,2,1,""],remove_zone_quick_veto:[5,2,1,""],request_hvac_update:[5,2,1,""],set_holiday_mode:[5,2,1,""],set_hot_water_operating_mode:[5,2,1,""],set_hot_water_setpoint_temperature:[5,2,1,""],set_quick_mode:[5,2,1,""],set_room_operating_mode:[5,2,1,""],set_room_quick_veto:[5,2,1,""],set_room_setpoint_temperature:[5,2,1,""],set_zone_operating_mode:[5,2,1,""],set_zone_quick_veto:[5,2,1,""],set_zone_setback_temperature:[5,2,1,""],set_zone_setpoint_temperature:[5,2,1,""]},pymultimatic:{api:[2,0,0,"-"],model:[3,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","data","Python data"],"4":["py","exception","Python exception"],"5":["py","function","Python function"],"6":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:data","4":"py:exception","5":"py:function","6":"py:attribute"},terms:{"4xx":2,"5xx":2,"case":[0,3,4],"class":[0,2,3,4,5],"default":[1,4],"float":[0,2,3,4,5],"function":[0,2,4],"int":[2,4],"long":3,"new":[2,5],"return":[0,2,3,4,5],"short":3,"switch":4,"throw":5,"true":[0,2,4,5],"try":[0,2,5],"while":5,For:[2,4],The:[0,2,3,4,5],There:[0,3,4,5],Use:4,Used:0,Will:0,abl:2,about:[0,3,4,5],absolut:3,absolute_minut:3,accept:5,accord:[4,5],account:4,action:2,activ:[0,2,4,5],active_funct:0,active_mod:[0,4],activemod:[0,1],actual:[0,4,5],advanc:4,affect:4,after:4,again:5,all:[0,2,4],allow:[0,5],also:[0,2,4],alter:5,alwai:[0,2,4],ambisens:0,ani:[0,2,5],anymor:0,anyth:0,api:[0,1,3,4,5],apiconnector:[2,5],apierror:[2,5],app:[0,3,4],appli:[0,4],applic:[0,2,4],ask:[2,3],assign:0,associ:[2,5],asynchron:5,authent:[2,5],auto:[0,3,4],automat:[2,4],avail:[0,3,4],awar:0,back:[0,4],bar:3,base:[0,4],basic:[0,2,3,5],batteri:0,battery_low:0,been:4,befor:[2,4,5],being:4,below:0,between:4,bit:0,boiler:[0,2,3],boiler_statu:0,boilerstatu:[0,1,5],bool:[0,2,3,4,5],boost:0,bring:4,button:0,call:[2,5],can:[0,3,4,5],cancel:4,cannot:0,certain:4,chang:[4,5],check:[2,3,4],child:2,child_lock:0,chosen:2,circuit:4,circul:[1,2,4,5],circulation_configur:2,circulation_timeprogram:2,classmethod:4,clear:2,code:[2,3],com:[2,4],come:[2,3,4],comfort:4,common:0,commun:2,compar:3,complex:4,compon:[1,2,3,4,5],configur:[0,2,3,4,5],connect:[0,3],connector:1,consider:4,contain:2,control:[0,4],conveni:[3,5],cooki:[2,5],cookie_file_nam:2,cool:[2,4],correct:5,correspond:[3,4],costli:5,cours:0,creat:2,current:[0,2,3,4,5],current_mod:4,current_temperatur:[0,3],customiz:4,cylind:4,dai:[0,2,3,4,5],data:[0,2,4,5],date:[2,3,4,5],datetim:[2,3,4,5],deactiv:4,defin:[3,4],delet:[2,5],delete_repeat:2,depend:5,descript:3,desir:[4,5],detail:2,devic:[1,2,3],device_id:2,device_nam:3,device_typ:0,dhw:[2,4],dhw_id:[2,5],dict:[2,3],differ:4,directli:[0,3],document:4,doe:5,doesn:[0,4,5],doing:0,domest:[2,4,5],don:5,done:[2,3,5],durat:[2,4],dure:3,earli:4,effect:5,elearn:4,els:4,embed:2,emf:2,emf_report:2,emf_report_devic:2,end:[3,4,5],end_dat:[2,4,5],energy_typ:2,ensur:5,equal:3,error:[0,1,5],etc:2,exampl:4,except:2,exist:2,expir:4,facil:2,facilities_default_set:2,facilities_detail:2,facilities_installer_info:2,facilities_list:2,facilities_set:2,facilities_statu:2,fals:[2,4,5],file:2,file_path:[2,5],files_path:2,find:0,first:[2,4],flag:3,follow:2,for_dhw:4,for_room:4,for_zon:4,forc:5,force_login:[2,5],format:[2,3],found:4,from:[0,2,3,4,5],frost:[4,5],full:[2,3,5],futur:4,gener:[2,4],get:[0,2,3,4,5],get_active_mode_circul:0,get_active_mode_hot_wat:0,get_active_mode_room:0,get_active_mode_zon:0,get_circul:5,get_for:3,get_hot_wat:5,get_room:5,get_system:5,get_zon:5,given:[0,3,5],goe:[0,2],going:4,group:[0,2,4],handl:[0,2,5],has:4,have:[2,4,5],heat:[0,2,4],help:5,helper:4,here:[0,2,5],highest:4,hint:3,holidai:[0,2,4,5],holiday_mod:[0,2],holidaymod:[0,1,2,5],hot:[1,2,4,5],hot_wat:[0,2],hot_water_configur:2,hot_water_operating_mod:2,hot_water_temperature_setpoint:2,hot_water_timeprogram:2,hotwat:[0,2,4,5],hotwater_boost:4,hotwater_temperature_setpoint:2,hour:[2,3,4],http:[2,4,5],humid:0,hvac:[2,5],hvac_upd:2,immedi:0,impact:4,index:5,indic:[0,4],infopool:4,inform:[0,5],initi:3,insid:0,instal:[2,4],interact:5,internet:3,interpret:[0,4],invalid:2,is_act:4,is_appli:[4,5],is_error:3,is_init:3,is_onlin:3,is_outd:3,is_pend:[3,5],is_sync:3,is_up_to_d:3,itself:0,json:2,keep:4,know:[3,4],last:3,let:4,level:[1,4],like:[3,4],link:[3,4],list:[0,2,3,4,5],littl:5,live:2,live_report:2,live_report_devic:2,locat:2,lock:[0,2],log:[2,5],login:[2,5],logout:[2,5],low:[0,1],lowest:4,mai:[0,4,5],main:0,maintain:4,make:4,manag:5,mandatori:2,manipul:0,manual:[0,2,4,5],map:3,max:[0,2,4],max_target_temp:0,mean:[0,2,4,5],messag:2,meter:2,method:2,min:0,min_target_temp:0,minut:[0,2,3,4,5],mobil:[0,3,4],mode:[0,1,2,3,5],model:[0,1,2,4,5],modul:2,more:3,most:[3,4,5],name:[0,2,3,4,5],necessari:5,necessarili:4,need:2,new_mod:5,new_token:2,newli:4,next:[3,4],night:[0,2,4,5],none:[0,2,3,4,5],nor:0,note:[0,4],now:2,number:[0,2,5],occur:[2,3,5],off:[0,4],offset:2,often:5,onc:4,one:[0,2,4],one_day_at_hom:4,one_day_awai:4,onli:[0,2,3,4],online_statu:3,open:0,oper:[0,2,4,5],operating_instruct:4,operating_mod:0,operatingmod:[0,1,5],option:[0,2,3,4,5],order:[2,3],other:2,otherwis:[2,4,5],out:[2,5],outdat:[2,3],outdoor:[0,2],outdoor_temperatur:0,outsid:4,overrid:5,overview:2,paramet:[0,2,3,4,5],parti:4,pass:[0,2],password:[2,5],path:[2,5],payload:[1,5],pdf:4,pend:3,period:[3,4],photovolta:2,physic:0,pick:0,place:4,placehold:2,pleas:[2,4],popul:[0,4],possibl:4,post:2,pre:4,preced:4,present:0,preset:4,press:0,pressur:3,previous:2,process:5,program:3,programm:4,properti:[0,2,3,4],protect:[4,5],provid:5,put:2,pymultimat:[0,2,3,4,5],qm_holidai:4,qm_hotwater_boost:4,qm_one_day_at_hom:4,qm_one_day_awai:4,qm_parti:4,qm_quick_veto:4,qm_system_off:4,qm_ventilation_boost:4,queri:2,quick:[0,2,4,5],quick_mod:[0,2,5],quick_veto:[0,4,5],quickli:4,quickmod:[0,1,2,5],quickveto:[0,1,2,5],quit:4,radiat:0,radio_out_of_reach:0,rais:2,raw:2,rbr:0,rbr_installation_statu:2,rbr_underfloor_heating_statu:2,reach:[0,3,4],read:5,real:[0,4],realli:0,receiv:[0,2],reconnect:2,reduc:5,reflect:[0,3],regardless:2,remain:[4,5],remaining_dur:4,remov:5,remove_holiday_mod:5,remove_quick_mod:5,remove_room_quick_veto:5,remove_zone_quick_veto:5,repeat:2,repeater_nam:2,report:2,report_id:2,repres:[0,3,4],request:[2,5],request_hvac_upd:5,requir:[2,5],resolv:2,resourc:3,resource_link:3,resourcest:3,respons:2,result:2,right:3,room:[1,2,3,4,5],room_child_lock:2,room_configur:2,room_device_nam:2,room_id:[0,5],room_index:2,room_nam:2,room_operating_mod:2,room_quick_veto:2,room_temperature_setpoint:2,room_timeprogram:2,run:[0,4],same:5,sate:3,search_dat:3,second:2,see:[3,5],selector:0,send:2,sent:3,serial:[0,2],serial_numb:2,serial_number_file_nam:2,set:[0,2,3,4,5],set_holiday_mod:5,set_hot_water_operating_mod:5,set_hot_water_setpoint_temperatur:5,set_quick_mod:5,set_room:0,set_room_operating_mod:5,set_room_quick_veto:5,set_room_setpoint_temperatur:5,set_ventilation_day_level:2,set_ventilation_night_level:2,set_ventilation_operating_mod:2,set_zon:0,set_zone_operating_mod:5,set_zone_quick_veto:5,set_zone_setback_temperatur:5,set_zone_setpoint_temperatur:5,setback:2,setpoint:2,settingmod:[1,3],sgtin:[0,2],should:[0,3,5],side:3,simpli:5,sinc:[0,4,5],six:4,skip:5,slot:4,smart:2,smartphon:2,smartphone_id:[2,5],some:[2,5],someth:2,somewher:4,special:0,specif:[2,4],standbi:0,start:[2,3,4,5],start_dat:[2,4,5],start_tim:3,state:3,statu:[0,2,3],status_cod:3,store:[2,5],str:[0,2,3,4,5],sub_mod:4,succeed:[2,5],sundai:4,swallow:5,sync:3,synchron:5,syncstat:[1,5],system:[1,2,3,4,5],system_configur:2,system_datetim:2,system_holiday_mod:2,system_off:4,system_paramet:2,system_quickmod:2,system_statu:[0,2],systemmanag:1,systemstatu:[0,1],take:[4,5],talk:3,target:[0,2,3,4,5],target_min_temperatur:0,target_temperatur:[0,3,4],tell:4,temp:4,temperatur:[0,2,3,4,5],thei:4,them:0,thermostat:0,thi:[0,2,3,4,5],think:5,through:[0,3,4,5],thrown:2,time:[0,3,4,5],time_program:0,time_rang:2,timeperiodset:[1,4],timeprogram:[0,1,2,4],timeprogramdai:1,timestamp:3,titl:3,todai:4,togeth:4,token:2,too:5,tri:4,two:5,type:[0,2,3,4,5],under:2,underfloor:2,until:[4,5],updat:[2,3,5],update_statu:3,url:[1,5],use:[0,2,5],used:[0,2,3,4],user:[0,2,4,5],using:[3,4],vaillant:[0,2,3,4,5],valu:[0,3,4],valv:0,ventil:[2,4],ventilation_boost:4,ventilation_configur:2,ventilation_id:2,ventilation_timeprogram:2,veto:[0,4,5],via:0,vr50:0,vr51:0,vr52:0,vrc700:[0,4],vrc:5,wai:[0,4,5],want:[0,5],water:[1,2,3,4,5],water_pressur:3,week:3,went:2,what:[0,3,4,5],when:[2,3,4],where:[2,3,5],whether:[4,5],which:[2,4],window:0,window_open:0,wise:[4,5],within:4,without:[4,5],won:[4,5],work:4,workaround:5,wrong:2,yesterdai:5,you:[0,3,4,5],your:[3,4,5],zone:[1,2,4,5],zone_configur:2,zone_cooling_configur:2,zone_cooling_manual_setpoint_temperatur:2,zone_cooling_mod:2,zone_cooling_setpoint_temperatur:2,zone_cooling_timeprogram:2,zone_heating_configur:2,zone_heating_mod:2,zone_heating_setback_temperatur:2,zone_heating_setpoint_temperatur:2,zone_heating_timeprogram:2,zone_id:[0,2,5],zone_nam:2,zone_operating_mod:2,zone_quick_veto:2,zone_temperature_setback:2,zone_temperature_setpoint:2},titles:["Components","Index","Low Level Connector","Model","Modes","SystemManager"],titleterms:{"default":2,activemod:4,api:2,boilerstatu:3,circul:0,compon:0,connector:2,devic:0,error:[2,3],holidaymod:4,hot:0,index:1,level:2,low:2,mode:4,model:3,operatingmod:4,payload:2,quickmod:4,quickveto:4,room:0,settingmod:4,syncstat:3,system:0,systemmanag:5,systemstatu:3,timeperiodset:3,timeprogram:3,timeprogramdai:3,url:2,water:0,zone:0}})