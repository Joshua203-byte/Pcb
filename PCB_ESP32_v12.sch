<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.7.0">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.1" unitdist="inch" unit="inch" style="lines" multiple="1" display="no" altdistance="0.01" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="no" active="no"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="no" active="no"/>
<layer number="17" name="Pads" color="2" fill="1" visible="no" active="no"/>
<layer number="18" name="Vias" color="2" fill="1" visible="no" active="no"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="no" active="no"/>
<layer number="20" name="Dimension" color="24" fill="1" visible="no" active="no"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="25" name="tNames" color="7" fill="1" visible="no" active="no"/>
<layer number="26" name="bNames" color="7" fill="1" visible="no" active="no"/>
<layer number="27" name="tValues" color="7" fill="1" visible="no" active="no"/>
<layer number="28" name="bValues" color="7" fill="1" visible="no" active="no"/>
<layer number="29" name="tStop" color="7" fill="3" visible="no" active="no"/>
<layer number="30" name="bStop" color="7" fill="6" visible="no" active="no"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="no"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="no"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="no"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="no"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="no"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="no"/>
<layer number="37" name="tTest" color="7" fill="1" visible="no" active="no"/>
<layer number="38" name="bTest" color="7" fill="1" visible="no" active="no"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="no" active="no"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="no" active="no"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="no" active="no"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="no" active="no"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="no" active="no"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="no"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="no"/>
<layer number="46" name="Milling" color="3" fill="1" visible="no" active="no"/>
<layer number="47" name="Measures" color="7" fill="1" visible="no" active="no"/>
<layer number="48" name="Document" color="7" fill="1" visible="no" active="no"/>
<layer number="49" name="Reference" color="7" fill="1" visible="no" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="88" name="SimResults" color="9" fill="1" visible="yes" active="yes"/>
<layer number="89" name="SimProbes" color="9" fill="1" visible="yes" active="yes"/>
<layer number="90" name="Modules" color="5" fill="1" visible="yes" active="yes"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="255" name="Undefined" color="7" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="PCB_PBL_Semiconductores">
<description>Libreria PBL Semiconductores (agujero pasante, grabado a mano)</description>
<packages>
<package name="SOCKET_1X06">
<description>Tira hembra 1x6, paso 2.54, taladro 0.9, pad 2.0</description>
<pad name="1" x="0" y="0" drill="0.9" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="0.9" diameter="2" shape="round"/>
<pad name="3" x="0" y="-5.08" drill="0.9" diameter="2" shape="round"/>
<pad name="4" x="0" y="-7.62" drill="0.9" diameter="2" shape="round"/>
<pad name="5" x="0" y="-10.16" drill="0.9" diameter="2" shape="round"/>
<pad name="6" x="0" y="-12.7" drill="0.9" diameter="2" shape="round"/>
<wire x1="-1.27" y1="1.27" x2="1.27" y2="1.27" width="0.2" layer="21"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-13.97" width="0.2" layer="21"/>
<wire x1="1.27" y1="-13.97" x2="-1.27" y2="-13.97" width="0.2" layer="21"/>
<wire x1="-1.27" y1="-13.97" x2="-1.27" y2="1.27" width="0.2" layer="21"/>
<text x="2" y="0.3" size="0.8" layer="21">1</text>
<text x="0" y="2.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-15.3" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="SOCKET_1X10">
<description>Tira hembra 1x10, paso 2.54, taladro 0.9, pad 2.0</description>
<pad name="1" x="0" y="0" drill="0.9" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="0.9" diameter="2" shape="round"/>
<pad name="3" x="0" y="-5.08" drill="0.9" diameter="2" shape="round"/>
<pad name="4" x="0" y="-7.62" drill="0.9" diameter="2" shape="round"/>
<pad name="5" x="0" y="-10.16" drill="0.9" diameter="2" shape="round"/>
<pad name="6" x="0" y="-12.7" drill="0.9" diameter="2" shape="round"/>
<pad name="7" x="0" y="-15.24" drill="0.9" diameter="2" shape="round"/>
<pad name="8" x="0" y="-17.78" drill="0.9" diameter="2" shape="round"/>
<pad name="9" x="0" y="-20.32" drill="0.9" diameter="2" shape="round"/>
<pad name="10" x="0" y="-22.86" drill="0.9" diameter="2" shape="round"/>
<wire x1="-1.27" y1="1.27" x2="1.27" y2="1.27" width="0.2" layer="21"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-24.13" width="0.2" layer="21"/>
<wire x1="1.27" y1="-24.13" x2="-1.27" y2="-24.13" width="0.2" layer="21"/>
<wire x1="-1.27" y1="-24.13" x2="-1.27" y2="1.27" width="0.2" layer="21"/>
<text x="2" y="0.3" size="0.8" layer="21">1</text>
<text x="0" y="2.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-25.46" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="MALE_1X03">
<description>Tira macho 1x3, paso 2.54, taladro 1.0, pad 2.0</description>
<pad name="1" x="0" y="0" drill="1" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="1" diameter="2" shape="round"/>
<pad name="3" x="0" y="-5.08" drill="1" diameter="2" shape="round"/>
<wire x1="-1.27" y1="1.27" x2="1.27" y2="1.27" width="0.2" layer="21"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-6.35" width="0.2" layer="21"/>
<wire x1="1.27" y1="-6.35" x2="-1.27" y2="-6.35" width="0.2" layer="21"/>
<wire x1="-1.27" y1="-6.35" x2="-1.27" y2="1.27" width="0.2" layer="21"/>
<text x="2" y="0.3" size="0.8" layer="21">1</text>
<text x="0" y="2.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-7.68" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="MALE_1X10">
<description>MALE_1X10</description>
<pad name="1" x="0" y="0" drill="1" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="1" diameter="2" shape="round"/>
<pad name="3" x="0" y="-5.08" drill="1" diameter="2" shape="round"/>
<pad name="4" x="0" y="-7.62" drill="1" diameter="2" shape="round"/>
<pad name="5" x="0" y="-10.16" drill="1" diameter="2" shape="round"/>
<pad name="6" x="0" y="-12.7" drill="1" diameter="2" shape="round"/>
<pad name="7" x="0" y="-15.24" drill="1" diameter="2" shape="round"/>
<pad name="8" x="0" y="-17.78" drill="1" diameter="2" shape="round"/>
<pad name="9" x="0" y="-20.32" drill="1" diameter="2" shape="round"/>
<pad name="10" x="0" y="-22.86" drill="1" diameter="2" shape="round"/>
<wire x1="-1.27" y1="1.27" x2="1.27" y2="1.27" width="0.2" layer="21"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-24.13" width="0.2" layer="21"/>
<wire x1="1.27" y1="-24.13" x2="-1.27" y2="-24.13" width="0.2" layer="21"/>
<wire x1="-1.27" y1="-24.13" x2="-1.27" y2="1.27" width="0.2" layer="21"/>
<text x="2" y="0.3" size="0.8" layer="21">1</text>
<text x="0" y="2.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-25.46" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="MALE_1X08">
<description>MALE_1X08</description>
<pad name="1" x="0" y="0" drill="1" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="1" diameter="2" shape="round"/>
<pad name="3" x="0" y="-5.08" drill="1" diameter="2" shape="round"/>
<pad name="4" x="0" y="-7.62" drill="1" diameter="2" shape="round"/>
<pad name="5" x="0" y="-10.16" drill="1" diameter="2" shape="round"/>
<pad name="6" x="0" y="-12.7" drill="1" diameter="2" shape="round"/>
<pad name="7" x="0" y="-15.24" drill="1" diameter="2" shape="round"/>
<pad name="8" x="0" y="-17.78" drill="1" diameter="2" shape="round"/>
<wire x1="-1.27" y1="1.27" x2="1.27" y2="1.27" width="0.2" layer="21"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-19.05" width="0.2" layer="21"/>
<wire x1="1.27" y1="-19.05" x2="-1.27" y2="-19.05" width="0.2" layer="21"/>
<wire x1="-1.27" y1="-19.05" x2="-1.27" y2="1.27" width="0.2" layer="21"/>
<text x="2" y="0.3" size="0.8" layer="21">1</text>
<text x="0" y="2.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-20.38" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="MALE_1X02">
<description>Tira macho 1x2, paso 2.54, taladro 1.0, pad 2.0</description>
<pad name="1" x="0" y="0" drill="1" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="1" diameter="2" shape="round"/>
<wire x1="-1.27" y1="1.27" x2="1.27" y2="1.27" width="0.2" layer="21"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-3.81" width="0.2" layer="21"/>
<wire x1="1.27" y1="-3.81" x2="-1.27" y2="-3.81" width="0.2" layer="21"/>
<wire x1="-1.27" y1="-3.81" x2="-1.27" y2="1.27" width="0.2" layer="21"/>
<text x="2" y="0.3" size="0.8" layer="21">1</text>
<text x="0" y="2.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-5.14" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="ESP32_DEVKIT38">
<description>ESP32 DevKitC 38 pines en dos tiras hembra 1x19, filas a 25.40 mm (MEDIR la tuya)</description>
<pad name="1" x="0" y="0" drill="0.9" diameter="2" shape="square"/>
<pad name="2" x="0" y="-2.54" drill="0.9" diameter="2" shape="round"/>
<pad name="3" x="0" y="-5.08" drill="0.9" diameter="2" shape="round"/>
<pad name="4" x="0" y="-7.62" drill="0.9" diameter="2" shape="round"/>
<pad name="5" x="0" y="-10.16" drill="0.9" diameter="2" shape="round"/>
<pad name="6" x="0" y="-12.7" drill="0.9" diameter="2" shape="round"/>
<pad name="7" x="0" y="-15.24" drill="0.9" diameter="2" shape="round"/>
<pad name="8" x="0" y="-17.78" drill="0.9" diameter="2" shape="round"/>
<pad name="9" x="0" y="-20.32" drill="0.9" diameter="2" shape="round"/>
<pad name="10" x="0" y="-22.86" drill="0.9" diameter="2" shape="round"/>
<pad name="11" x="0" y="-25.4" drill="0.9" diameter="2" shape="round"/>
<pad name="12" x="0" y="-27.94" drill="0.9" diameter="2" shape="round"/>
<pad name="13" x="0" y="-30.48" drill="0.9" diameter="2" shape="round"/>
<pad name="14" x="0" y="-33.02" drill="0.9" diameter="2" shape="round"/>
<pad name="15" x="0" y="-35.56" drill="0.9" diameter="2" shape="round"/>
<pad name="16" x="0" y="-38.1" drill="0.9" diameter="2" shape="round"/>
<pad name="17" x="0" y="-40.64" drill="0.9" diameter="2" shape="round"/>
<pad name="18" x="0" y="-43.18" drill="0.9" diameter="2" shape="round"/>
<pad name="19" x="0" y="-45.72" drill="0.9" diameter="2" shape="round"/>
<pad name="38" x="25.4" y="0" drill="0.9" diameter="2" shape="round"/>
<pad name="37" x="25.4" y="-2.54" drill="0.9" diameter="2" shape="round"/>
<pad name="36" x="25.4" y="-5.08" drill="0.9" diameter="2" shape="round"/>
<pad name="35" x="25.4" y="-7.62" drill="0.9" diameter="2" shape="round"/>
<pad name="34" x="25.4" y="-10.16" drill="0.9" diameter="2" shape="round"/>
<pad name="33" x="25.4" y="-12.7" drill="0.9" diameter="2" shape="round"/>
<pad name="32" x="25.4" y="-15.24" drill="0.9" diameter="2" shape="round"/>
<pad name="31" x="25.4" y="-17.78" drill="0.9" diameter="2" shape="round"/>
<pad name="30" x="25.4" y="-20.32" drill="0.9" diameter="2" shape="round"/>
<pad name="29" x="25.4" y="-22.86" drill="0.9" diameter="2" shape="round"/>
<pad name="28" x="25.4" y="-25.4" drill="0.9" diameter="2" shape="round"/>
<pad name="27" x="25.4" y="-27.94" drill="0.9" diameter="2" shape="round"/>
<pad name="26" x="25.4" y="-30.48" drill="0.9" diameter="2" shape="round"/>
<pad name="25" x="25.4" y="-33.02" drill="0.9" diameter="2" shape="round"/>
<pad name="24" x="25.4" y="-35.56" drill="0.9" diameter="2" shape="round"/>
<pad name="23" x="25.4" y="-38.1" drill="0.9" diameter="2" shape="round"/>
<pad name="22" x="25.4" y="-40.64" drill="0.9" diameter="2" shape="round"/>
<pad name="21" x="25.4" y="-43.18" drill="0.9" diameter="2" shape="round"/>
<pad name="20" x="25.4" y="-45.72" drill="0.9" diameter="2" shape="round"/>
<wire x1="-1.9" y1="4.5" x2="27.3" y2="4.5" width="0.2" layer="21"/>
<wire x1="27.3" y1="4.5" x2="27.3" y2="-54.72" width="0.2" layer="21"/>
<wire x1="27.3" y1="-54.72" x2="-1.9" y2="-54.72" width="0.2" layer="21"/>
<wire x1="-1.9" y1="-54.72" x2="-1.9" y2="4.5" width="0.2" layer="21"/>
<wire x1="-1.9" y1="4.5" x2="27.3" y2="4.5" width="0.2" layer="51"/>
<wire x1="27.3" y1="4.5" x2="27.3" y2="-54.72" width="0.2" layer="51"/>
<wire x1="27.3" y1="-54.72" x2="-1.9" y2="-54.72" width="0.2" layer="51"/>
<wire x1="-1.9" y1="-54.72" x2="-1.9" y2="4.5" width="0.2" layer="51"/>
<wire x1="8.7" y1="-54.72" x2="16.7" y2="-54.72" width="0.2" layer="21"/>
<wire x1="16.7" y1="-54.72" x2="16.7" y2="-51.72" width="0.2" layer="21"/>
<wire x1="16.7" y1="-51.72" x2="8.7" y2="-51.72" width="0.2" layer="21"/>
<wire x1="8.7" y1="-51.72" x2="8.7" y2="-54.72" width="0.2" layer="21"/>
<text x="12.7" y="-50.72" size="1" layer="21">USB</text>
<text x="12.7" y="2" size="1" layer="21">ANTENA</text>
<text x="2" y="0" size="0.8" layer="21">3V3</text>
<text x="2" y="-45.72" size="0.8" layer="21">5V</text>
<text x="0" y="6" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-7.2" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="TERM2_5MM">
<description>Bornera de tornillo 2 pines, paso 5.08, taladro 1.3, pad 3.0</description>
<pad name="1" x="0" y="0" drill="1.3" diameter="3" shape="square"/>
<pad name="2" x="5.08" y="0" drill="1.3" diameter="3" shape="round"/>
<wire x1="-2.6" y1="3.6" x2="7.7" y2="3.6" width="0.2" layer="21"/>
<wire x1="7.7" y1="3.6" x2="7.7" y2="-3.6" width="0.2" layer="21"/>
<wire x1="7.7" y1="-3.6" x2="-2.6" y2="-3.6" width="0.2" layer="21"/>
<wire x1="-2.6" y1="-3.6" x2="-2.6" y2="3.6" width="0.2" layer="21"/>
<text x="0" y="4.5" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-5.7" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="RES_V">
<description>Resistencia montada vertical, separacion 3.81, taladro 0.8, pad 2.4</description>
<pad name="1" x="0" y="0" drill="0.8" diameter="2.4" shape="square"/>
<pad name="2" x="3.81" y="0" drill="0.8" diameter="2.4" shape="round"/>
<circle x="0" y="0" radius="1.7" width="0.2" layer="21"/>
<wire x1="0" y1="0" x2="3.81" y2="0" width="0.1" layer="51"/>
<text x="0" y="2.5" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-3.7" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="RES_H_T">
<description>Resistencia de carga 1/2 W acostada, separacion 12.7; pad 1 (3.0/1.3): aqui tambien entra el cable NO del rele; pad 2 2.4/0.8</description>
<pad name="1" x="0" y="0" drill="1.3" diameter="3" shape="square"/>
<pad name="2" x="12.7" y="0" drill="0.8" diameter="2.4" shape="round"/>
<wire x1="-1.9" y1="1.9" x2="14.6" y2="1.9" width="0.2" layer="21"/>
<wire x1="14.6" y1="1.9" x2="14.6" y2="-1.9" width="0.2" layer="21"/>
<wire x1="14.6" y1="-1.9" x2="-1.9" y2="-1.9" width="0.2" layer="21"/>
<wire x1="-1.9" y1="-1.9" x2="-1.9" y2="1.9" width="0.2" layer="21"/>
<wire x1="1.85" y1="1.75" x2="10.85" y2="1.75" width="0.2" layer="21"/>
<wire x1="10.85" y1="1.75" x2="10.85" y2="-1.75" width="0.2" layer="21"/>
<wire x1="10.85" y1="-1.75" x2="1.85" y2="-1.75" width="0.2" layer="21"/>
<wire x1="1.85" y1="-1.75" x2="1.85" y2="1.75" width="0.2" layer="21"/>
<text x="-0.9" y="2.3" size="0.8" layer="21">NO</text>
<text x="0" y="2.6" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-3.8" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="CAP_5MM">
<description>Capacitor poliester, paso 5.08, taladro 0.8, pad 2.4</description>
<pad name="1" x="0" y="0" drill="0.8" diameter="2.4" shape="square"/>
<pad name="2" x="5.08" y="0" drill="0.8" diameter="2.4" shape="round"/>
<wire x1="-1.6" y1="1.8" x2="6.7" y2="1.8" width="0.2" layer="21"/>
<wire x1="6.7" y1="1.8" x2="6.7" y2="-1.8" width="0.2" layer="21"/>
<wire x1="6.7" y1="-1.8" x2="-1.6" y2="-1.8" width="0.2" layer="21"/>
<wire x1="-1.6" y1="-1.8" x2="-1.6" y2="1.8" width="0.2" layer="21"/>
<text x="0" y="2.6" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-3.8" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="JPAD">
<description>Pad exclusivo para cable puente (cara de componentes), taladro 1.0, pad 2.5</description>
<pad name="1" x="0" y="0" drill="1" diameter="2.5" shape="round"/>
<circle x="0" y="0" radius="1.6" width="0.2" layer="21"/>
<text x="0" y="2.3" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-3.5" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="CAP_E_2_54">
<description>Capacitor electrolitico radial 2.54, pin 1 = +, taladro 0.8</description>
<pad name="1" x="0" y="0" drill="0.8" diameter="2" shape="square"/>
<pad name="2" x="2.54" y="0" drill="0.8" diameter="2" shape="round"/>
<circle x="1.27" y="0" radius="3.4" width="0.2" layer="21"/>
<text x="-1" y="1.8" size="1.2" layer="21">+</text>
<text x="0" y="4.2" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-5.4" size="0.8" layer="27">&gt;VALUE</text>
</package>
<package name="WIREPAD">
<description>Pad para cable al modulo de reles, taladro 1.3, pad 3.0</description>
<pad name="1" x="0" y="0" drill="1.3" diameter="3" shape="round"/>
<circle x="0" y="0" radius="1.9" width="0.2" layer="21"/>
<text x="0" y="2.6" size="1" layer="25">&gt;NAME</text>
<text x="0" y="-3.8" size="0.8" layer="27">&gt;VALUE</text>
</package>
</packages>
<symbols>
<symbol name="SYM_ESP32">
<wire x1="0" y1="2.54" x2="22.86" y2="2.54" width="0.254" layer="94"/>
<wire x1="22.86" y1="2.54" x2="22.86" y2="-48.26" width="0.254" layer="94"/>
<wire x1="22.86" y1="-48.26" x2="0" y2="-48.26" width="0.254" layer="94"/>
<wire x1="0" y1="-48.26" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-50.546" size="1.778" layer="96">&gt;VALUE</text>
<pin name="3V3" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="EN" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="SVP" x="-2.54" y="-5.08" length="short" direction="pas"/>
<pin name="SVN" x="-2.54" y="-7.62" length="short" direction="pas"/>
<pin name="IO34" x="-2.54" y="-10.16" length="short" direction="pas"/>
<pin name="IO35" x="-2.54" y="-12.7" length="short" direction="pas"/>
<pin name="IO32" x="-2.54" y="-15.24" length="short" direction="pas"/>
<pin name="IO33" x="-2.54" y="-17.78" length="short" direction="pas"/>
<pin name="IO25" x="-2.54" y="-20.32" length="short" direction="pas"/>
<pin name="IO26" x="-2.54" y="-22.86" length="short" direction="pas"/>
<pin name="IO27" x="-2.54" y="-25.4" length="short" direction="pas"/>
<pin name="IO14" x="-2.54" y="-27.94" length="short" direction="pas"/>
<pin name="IO12" x="-2.54" y="-30.48" length="short" direction="pas"/>
<pin name="GND@1" x="-2.54" y="-33.02" length="short" direction="pas"/>
<pin name="IO13" x="-2.54" y="-35.56" length="short" direction="pas"/>
<pin name="SD2" x="-2.54" y="-38.1" length="short" direction="pas"/>
<pin name="SD3" x="-2.54" y="-40.64" length="short" direction="pas"/>
<pin name="CMD" x="-2.54" y="-43.18" length="short" direction="pas"/>
<pin name="5V" x="-2.54" y="-45.72" length="short" direction="pas"/>
<pin name="GND@2" x="25.4" y="0" length="short" direction="pas" rot="R180"/>
<pin name="IO23" x="25.4" y="-2.54" length="short" direction="pas" rot="R180"/>
<pin name="IO22" x="25.4" y="-5.08" length="short" direction="pas" rot="R180"/>
<pin name="TXD0" x="25.4" y="-7.62" length="short" direction="pas" rot="R180"/>
<pin name="RXD0" x="25.4" y="-10.16" length="short" direction="pas" rot="R180"/>
<pin name="IO21" x="25.4" y="-12.7" length="short" direction="pas" rot="R180"/>
<pin name="GND@3" x="25.4" y="-15.24" length="short" direction="pas" rot="R180"/>
<pin name="IO19" x="25.4" y="-17.78" length="short" direction="pas" rot="R180"/>
<pin name="IO18" x="25.4" y="-20.32" length="short" direction="pas" rot="R180"/>
<pin name="IO5" x="25.4" y="-22.86" length="short" direction="pas" rot="R180"/>
<pin name="IO17" x="25.4" y="-25.4" length="short" direction="pas" rot="R180"/>
<pin name="IO16" x="25.4" y="-27.94" length="short" direction="pas" rot="R180"/>
<pin name="IO4" x="25.4" y="-30.48" length="short" direction="pas" rot="R180"/>
<pin name="IO0" x="25.4" y="-33.02" length="short" direction="pas" rot="R180"/>
<pin name="IO2" x="25.4" y="-35.56" length="short" direction="pas" rot="R180"/>
<pin name="IO15" x="25.4" y="-38.1" length="short" direction="pas" rot="R180"/>
<pin name="SD1" x="25.4" y="-40.64" length="short" direction="pas" rot="R180"/>
<pin name="SD0" x="25.4" y="-43.18" length="short" direction="pas" rot="R180"/>
<pin name="CLK" x="25.4" y="-45.72" length="short" direction="pas" rot="R180"/>
</symbol>
<symbol name="SYM_ADS1115">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-25.4" width="0.254" layer="94"/>
<wire x1="12.7" y1="-25.4" x2="0" y2="-25.4" width="0.254" layer="94"/>
<wire x1="0" y1="-25.4" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-27.686" size="1.778" layer="96">&gt;VALUE</text>
<pin name="VDD" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="GND" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="SCL" x="-2.54" y="-5.08" length="short" direction="pas"/>
<pin name="SDA" x="-2.54" y="-7.62" length="short" direction="pas"/>
<pin name="ADDR" x="-2.54" y="-10.16" length="short" direction="pas"/>
<pin name="ALRT" x="-2.54" y="-12.7" length="short" direction="pas"/>
<pin name="AIN0" x="-2.54" y="-15.24" length="short" direction="pas"/>
<pin name="AIN1" x="-2.54" y="-17.78" length="short" direction="pas"/>
<pin name="AIN2" x="-2.54" y="-20.32" length="short" direction="pas"/>
<pin name="AIN3" x="-2.54" y="-22.86" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_SDCARD">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-15.24" width="0.254" layer="94"/>
<wire x1="12.7" y1="-15.24" x2="0" y2="-15.24" width="0.254" layer="94"/>
<wire x1="0" y1="-15.24" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-17.526" size="1.778" layer="96">&gt;VALUE</text>
<pin name="GND" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="VCC" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="MISO" x="-2.54" y="-5.08" length="short" direction="pas"/>
<pin name="MOSI" x="-2.54" y="-7.62" length="short" direction="pas"/>
<pin name="SCK" x="-2.54" y="-10.16" length="short" direction="pas"/>
<pin name="CS" x="-2.54" y="-12.7" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_DS3231">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-15.24" width="0.254" layer="94"/>
<wire x1="12.7" y1="-15.24" x2="0" y2="-15.24" width="0.254" layer="94"/>
<wire x1="0" y1="-15.24" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-17.526" size="1.778" layer="96">&gt;VALUE</text>
<pin name="32K" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="SQW" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="SCL" x="-2.54" y="-5.08" length="short" direction="pas"/>
<pin name="SDA" x="-2.54" y="-7.62" length="short" direction="pas"/>
<pin name="VCC" x="-2.54" y="-10.16" length="short" direction="pas"/>
<pin name="GND" x="-2.54" y="-12.7" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_RELAY_L">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="-7.62" x2="0" y2="-7.62" width="0.254" layer="94"/>
<wire x1="0" y1="-7.62" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-9.906" size="1.778" layer="96">&gt;VALUE</text>
<pin name="IN1" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="IN2" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="IN3" x="-2.54" y="-5.08" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_RELAY_RA">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="-7.62" x2="0" y2="-7.62" width="0.254" layer="94"/>
<wire x1="0" y1="-7.62" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-9.906" size="1.778" layer="96">&gt;VALUE</text>
<pin name="IN4" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="IN5" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="IN6" x="-2.54" y="-5.08" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_RELAY_RC">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="-5.08" x2="0" y2="-5.08" width="0.254" layer="94"/>
<wire x1="0" y1="-5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-7.366" size="1.778" layer="96">&gt;VALUE</text>
<pin name="IN7" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="IN8" x="-2.54" y="-2.54" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_RELAY_PWR">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="-5.08" x2="0" y2="-5.08" width="0.254" layer="94"/>
<wire x1="0" y1="-5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-7.366" size="1.778" layer="96">&gt;VALUE</text>
<pin name="5V" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="GND" x="-2.54" y="-2.54" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_DS18B20_HDR">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="-7.62" x2="0" y2="-7.62" width="0.254" layer="94"/>
<wire x1="0" y1="-7.62" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-9.906" size="1.778" layer="96">&gt;VALUE</text>
<pin name="VDD" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="DQ" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="GND" x="-2.54" y="-5.08" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_TESTPOINTS">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-7.62" width="0.254" layer="94"/>
<wire x1="12.7" y1="-7.62" x2="0" y2="-7.62" width="0.254" layer="94"/>
<wire x1="0" y1="-7.62" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-9.906" size="1.778" layer="96">&gt;VALUE</text>
<pin name="3V3" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="5V" x="-2.54" y="-2.54" length="short" direction="pas"/>
<pin name="GND" x="-2.54" y="-5.08" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_TERM2">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="-5.08" x2="0" y2="-5.08" width="0.254" layer="94"/>
<wire x1="0" y1="-5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-7.366" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="2" x="-2.54" y="-2.54" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_RLOAD">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="-5.08" x2="0" y2="-5.08" width="0.254" layer="94"/>
<wire x1="0" y1="-5.08" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-7.366" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-2.54" y="0" length="short" direction="pas"/>
<pin name="2" x="-2.54" y="-2.54" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_R">
<wire x1="-2.54" y1="-1.016" x2="2.54" y2="-1.016" width="0.254" layer="94"/>
<wire x1="2.54" y1="-1.016" x2="2.54" y2="1.016" width="0.254" layer="94"/>
<wire x1="2.54" y1="1.016" x2="-2.54" y2="1.016" width="0.254" layer="94"/>
<wire x1="-2.54" y1="1.016" x2="-2.54" y2="-1.016" width="0.254" layer="94"/>
<text x="-2.54" y="2.54" size="1.778" layer="95">&gt;NAME</text>
<text x="-2.54" y="-4.318" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-7.62" y="0" visible="off" length="short" direction="pas"/>
<pin name="2" x="7.62" y="0" visible="off" length="short" direction="pas" rot="R180"/>
</symbol>
<symbol name="SYM_C">
<wire x1="-0.635" y1="2.54" x2="-0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0.635" y1="2.54" x2="0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0" x2="-0.635" y2="0" width="0.254" layer="94"/>
<wire x1="0.635" y1="0" x2="2.54" y2="0" width="0.254" layer="94"/>
<text x="-2.54" y="2.54" size="1.778" layer="95">&gt;NAME</text>
<text x="-2.54" y="-4.318" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-7.62" y="0" visible="off" length="short" direction="pas"/>
<pin name="2" x="7.62" y="0" visible="off" length="short" direction="pas" rot="R180"/>
</symbol>
<symbol name="SYM_CP">
<wire x1="-0.635" y1="2.54" x2="-0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0.635" y1="2.54" x2="0.635" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0" x2="-0.635" y2="0" width="0.254" layer="94"/>
<wire x1="0.635" y1="0" x2="2.54" y2="0" width="0.254" layer="94"/>
<text x="-2.54" y="2.54" size="1.778" layer="95">&gt;NAME</text>
<text x="-2.54" y="-4.318" size="1.778" layer="96">&gt;VALUE</text>
<pin name="+" x="-7.62" y="0" visible="off" length="short" direction="pas"/>
<pin name="-" x="7.62" y="0" visible="off" length="short" direction="pas" rot="R180"/>
</symbol>
<symbol name="SYM_WIREPAD">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="-2.54" x2="0" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0" y1="-2.54" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-4.826" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-2.54" y="0" length="short" direction="pas"/>
</symbol>
<symbol name="SYM_JPAD">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="-2.54" x2="0" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0" y1="-2.54" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-4.826" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-2.54" y="0" length="short" direction="pas"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="ESP32" prefix="U" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_ESP32" x="0" y="0"/></gates>
<devices><device name="" package="ESP32_DEVKIT38"><connects>
<connect gate="G$1" pin="3V3" pad="1"/>
<connect gate="G$1" pin="EN" pad="2"/>
<connect gate="G$1" pin="SVP" pad="3"/>
<connect gate="G$1" pin="SVN" pad="4"/>
<connect gate="G$1" pin="IO34" pad="5"/>
<connect gate="G$1" pin="IO35" pad="6"/>
<connect gate="G$1" pin="IO32" pad="7"/>
<connect gate="G$1" pin="IO33" pad="8"/>
<connect gate="G$1" pin="IO25" pad="9"/>
<connect gate="G$1" pin="IO26" pad="10"/>
<connect gate="G$1" pin="IO27" pad="11"/>
<connect gate="G$1" pin="IO14" pad="12"/>
<connect gate="G$1" pin="IO12" pad="13"/>
<connect gate="G$1" pin="GND@1" pad="14"/>
<connect gate="G$1" pin="IO13" pad="15"/>
<connect gate="G$1" pin="SD2" pad="16"/>
<connect gate="G$1" pin="SD3" pad="17"/>
<connect gate="G$1" pin="CMD" pad="18"/>
<connect gate="G$1" pin="5V" pad="19"/>
<connect gate="G$1" pin="GND@2" pad="38"/>
<connect gate="G$1" pin="IO23" pad="37"/>
<connect gate="G$1" pin="IO22" pad="36"/>
<connect gate="G$1" pin="TXD0" pad="35"/>
<connect gate="G$1" pin="RXD0" pad="34"/>
<connect gate="G$1" pin="IO21" pad="33"/>
<connect gate="G$1" pin="GND@3" pad="32"/>
<connect gate="G$1" pin="IO19" pad="31"/>
<connect gate="G$1" pin="IO18" pad="30"/>
<connect gate="G$1" pin="IO5" pad="29"/>
<connect gate="G$1" pin="IO17" pad="28"/>
<connect gate="G$1" pin="IO16" pad="27"/>
<connect gate="G$1" pin="IO4" pad="26"/>
<connect gate="G$1" pin="IO0" pad="25"/>
<connect gate="G$1" pin="IO2" pad="24"/>
<connect gate="G$1" pin="IO15" pad="23"/>
<connect gate="G$1" pin="SD1" pad="22"/>
<connect gate="G$1" pin="SD0" pad="21"/>
<connect gate="G$1" pin="CLK" pad="20"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="ADS1115" prefix="U" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_ADS1115" x="0" y="0"/></gates>
<devices><device name="" package="SOCKET_1X10"><connects>
<connect gate="G$1" pin="VDD" pad="1"/>
<connect gate="G$1" pin="GND" pad="2"/>
<connect gate="G$1" pin="SCL" pad="3"/>
<connect gate="G$1" pin="SDA" pad="4"/>
<connect gate="G$1" pin="ADDR" pad="5"/>
<connect gate="G$1" pin="ALRT" pad="6"/>
<connect gate="G$1" pin="AIN0" pad="7"/>
<connect gate="G$1" pin="AIN1" pad="8"/>
<connect gate="G$1" pin="AIN2" pad="9"/>
<connect gate="G$1" pin="AIN3" pad="10"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="SDCARD" prefix="U" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_SDCARD" x="0" y="0"/></gates>
<devices><device name="" package="SOCKET_1X06"><connects>
<connect gate="G$1" pin="GND" pad="1"/>
<connect gate="G$1" pin="VCC" pad="2"/>
<connect gate="G$1" pin="MISO" pad="3"/>
<connect gate="G$1" pin="MOSI" pad="4"/>
<connect gate="G$1" pin="SCK" pad="5"/>
<connect gate="G$1" pin="CS" pad="6"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="DS3231" prefix="U" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_DS3231" x="0" y="0"/></gates>
<devices><device name="" package="SOCKET_1X06"><connects>
<connect gate="G$1" pin="32K" pad="1"/>
<connect gate="G$1" pin="SQW" pad="2"/>
<connect gate="G$1" pin="SCL" pad="3"/>
<connect gate="G$1" pin="SDA" pad="4"/>
<connect gate="G$1" pin="VCC" pad="5"/>
<connect gate="G$1" pin="GND" pad="6"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="RELAY_L" prefix="J" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_RELAY_L" x="0" y="0"/></gates>
<devices><device name="" package="MALE_1X03"><connects>
<connect gate="G$1" pin="IN1" pad="1"/>
<connect gate="G$1" pin="IN2" pad="2"/>
<connect gate="G$1" pin="IN3" pad="3"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="RELAY_RA" prefix="J" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_RELAY_RA" x="0" y="0"/></gates>
<devices><device name="" package="MALE_1X03"><connects>
<connect gate="G$1" pin="IN4" pad="1"/>
<connect gate="G$1" pin="IN5" pad="2"/>
<connect gate="G$1" pin="IN6" pad="3"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="RELAY_RC" prefix="J" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_RELAY_RC" x="0" y="0"/></gates>
<devices><device name="" package="MALE_1X02"><connects>
<connect gate="G$1" pin="IN7" pad="1"/>
<connect gate="G$1" pin="IN8" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="RELAY_PWR" prefix="J" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_RELAY_PWR" x="0" y="0"/></gates>
<devices><device name="" package="MALE_1X02"><connects>
<connect gate="G$1" pin="5V" pad="1"/>
<connect gate="G$1" pin="GND" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="DS18B20_HDR" prefix="J" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_DS18B20_HDR" x="0" y="0"/></gates>
<devices><device name="" package="MALE_1X03"><connects>
<connect gate="G$1" pin="VDD" pad="1"/>
<connect gate="G$1" pin="DQ" pad="2"/>
<connect gate="G$1" pin="GND" pad="3"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="TESTPOINTS" prefix="TP" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_TESTPOINTS" x="0" y="0"/></gates>
<devices><device name="" package="MALE_1X03"><connects>
<connect gate="G$1" pin="3V3" pad="1"/>
<connect gate="G$1" pin="5V" pad="2"/>
<connect gate="G$1" pin="GND" pad="3"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="TERM2" prefix="J" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_TERM2" x="0" y="0"/></gates>
<devices><device name="" package="TERM2_5MM"><connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="RLOAD" prefix="R" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_RLOAD" x="0" y="0"/></gates>
<devices><device name="" package="RES_H_T"><connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="R" prefix="R" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_R" x="0" y="0"/></gates>
<devices><device name="" package="RES_V"><connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="C" prefix="C" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_C" x="0" y="0"/></gates>
<devices><device name="" package="CAP_5MM"><connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="CP" prefix="C" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_CP" x="0" y="0"/></gates>
<devices><device name="" package="CAP_E_2_54"><connects>
<connect gate="G$1" pin="+" pad="1"/>
<connect gate="G$1" pin="-" pad="2"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="WIREPAD" prefix="W" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_WIREPAD" x="0" y="0"/></gates>
<devices><device name="" package="WIREPAD"><connects>
<connect gate="G$1" pin="1" pad="1"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
<deviceset name="JPAD" prefix="JP" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_JPAD" x="0" y="0"/></gates>
<devices><device name="" package="JPAD"><connects>
<connect gate="G$1" pin="1" pad="1"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="default" width="0" drill="0">
</class>
</classes>
<parts>
<part name="U1" library="PCB_PBL_Semiconductores" deviceset="ESP32" device="" value="ESP32 DevKitC 38 pines"/>
<part name="U2" library="PCB_PBL_Semiconductores" deviceset="ADS1115" device="" value="ADS1115 (modulo)"/>
<part name="U4" library="PCB_PBL_Semiconductores" deviceset="SDCARD" device="" value="Modulo microSD SPI"/>
<part name="U5" library="PCB_PBL_Semiconductores" deviceset="DS3231" device="" value="Modulo RTC DS3231"/>
<part name="J2" library="PCB_PBL_Semiconductores" deviceset="RELAY_L" device="" value="Reles IN1-IN3"/>
<part name="J6" library="PCB_PBL_Semiconductores" deviceset="RELAY_RA" device="" value="Reles IN4-IN6"/>
<part name="J7" library="PCB_PBL_Semiconductores" deviceset="RELAY_RC" device="" value="Reles IN7-IN8"/>
<part name="J5" library="PCB_PBL_Semiconductores" deviceset="RELAY_PWR" device="" value="Rele 5V y GND"/>
<part name="J3" library="PCB_PBL_Semiconductores" deviceset="DS18B20_HDR" device="" value="DS18B20"/>
<part name="TP1" library="PCB_PBL_Semiconductores" deviceset="TESTPOINTS" device="" value="Puntos de prueba"/>
<part name="J1" library="PCB_PBL_Semiconductores" deviceset="TERM2" device="" value="Panel"/>
<part name="J4" library="PCB_PBL_Semiconductores" deviceset="TERM2" device="" value="Celda referencia"/>
<part name="R1" library="PCB_PBL_Semiconductores" deviceset="R" device="" value="33k 1%"/>
<part name="R2" library="PCB_PBL_Semiconductores" deviceset="R" device="" value="10k 1%"/>
<part name="R3" library="PCB_PBL_Semiconductores" deviceset="R" device="" value="1k"/>
<part name="R4" library="PCB_PBL_Semiconductores" deviceset="R" device="" value="4.7k"/>
<part name="R_SH1" library="PCB_PBL_Semiconductores" deviceset="R" device="" value="1"/>
<part name="R_SH2" library="PCB_PBL_Semiconductores" deviceset="R" device="" value="1"/>
<part name="RL1" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="2.2"/>
<part name="COM1" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K1"/>
<part name="RL2" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="4.7"/>
<part name="COM2" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K2"/>
<part name="RL3" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="10"/>
<part name="COM3" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K3"/>
<part name="RL4" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="22"/>
<part name="COM4" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K4"/>
<part name="RL5" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="47"/>
<part name="COM5" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K5"/>
<part name="RL6" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="100"/>
<part name="COM6" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K6"/>
<part name="RL7" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="220"/>
<part name="COM7" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K7"/>
<part name="RL8" library="PCB_PBL_Semiconductores" deviceset="RLOAD" device="" value="470"/>
<part name="COM8" library="PCB_PBL_Semiconductores" deviceset="WIREPAD" device="" value="COM K8"/>
<part name="C1" library="PCB_PBL_Semiconductores" deviceset="C" device="" value="0.1u"/>
<part name="C4" library="PCB_PBL_Semiconductores" deviceset="CP" device="" value="10u 16V"/>
<part name="JP1A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 1 (SCL)"/>
<part name="JP1B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 1 (SCL)"/>
<part name="JP2A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 2 (LB)"/>
<part name="JP2B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 2 (LB)"/>
<part name="JP3A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 3 (3V3)"/>
<part name="JP3B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 3 (3V3)"/>
<part name="JP4A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 4 (3V3)"/>
<part name="JP4B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 4 (3V3)"/>
<part name="JP5A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 5 (GND)"/>
<part name="JP5B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 5 (GND)"/>
<part name="JP6A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 6 (GND)"/>
<part name="JP6B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 6 (GND)"/>
<part name="JP7A" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 7 (GND)"/>
<part name="JP7B" library="PCB_PBL_Semiconductores" deviceset="JPAD" device="" value="Puente 7 (GND)"/>
</parts>
<sheets>
<sheet>
<plain>
<text x="20" y="285" size="3" layer="97">PBL Semiconductores EE2002 - Monitor I-V de panel 1.5 W (ESP32 DevKitC)</text>
</plain>
<instances>
<instance part="U1" gate="G$1" x="60" y="266"/>
<instance part="U2" gate="G$1" x="170" y="266"/>
<instance part="U4" gate="G$1" x="170" y="224.6"/>
<instance part="U5" gate="G$1" x="170" y="193.36"/>
<instance part="J1" gate="G$1" x="170" y="162.12"/>
<instance part="J2" gate="G$1" x="170" y="141.04"/>
<instance part="J3" gate="G$1" x="170" y="117.42"/>
<instance part="J4" gate="G$1" x="170" y="93.8"/>
<instance part="J5" gate="G$1" x="170" y="72.72"/>
<instance part="J6" gate="G$1" x="170" y="51.64"/>
<instance part="J7" gate="G$1" x="170" y="28.02"/>
<instance part="TP1" gate="G$1" x="280" y="266"/>
<instance part="R1" gate="G$1" x="395" y="266"/>
<instance part="R2" gate="G$1" x="395" y="248"/>
<instance part="R3" gate="G$1" x="395" y="230"/>
<instance part="R4" gate="G$1" x="395" y="212"/>
<instance part="R_SH1" gate="G$1" x="395" y="194"/>
<instance part="R_SH2" gate="G$1" x="395" y="176"/>
<instance part="C1" gate="G$1" x="395" y="158"/>
<instance part="C4" gate="G$1" x="395" y="140"/>
<instance part="RL1" gate="G$1" x="280" y="242.38"/>
<instance part="RL2" gate="G$1" x="280" y="221.3"/>
<instance part="RL3" gate="G$1" x="280" y="200.22"/>
<instance part="RL4" gate="G$1" x="280" y="179.14"/>
<instance part="RL5" gate="G$1" x="280" y="158.06"/>
<instance part="RL6" gate="G$1" x="280" y="136.98"/>
<instance part="RL7" gate="G$1" x="280" y="115.9"/>
<instance part="RL8" gate="G$1" x="280" y="94.82"/>
<instance part="COM1" gate="G$1" x="395" y="122"/>
<instance part="COM2" gate="G$1" x="395" y="104"/>
<instance part="COM3" gate="G$1" x="395" y="86"/>
<instance part="COM4" gate="G$1" x="395" y="68"/>
<instance part="COM5" gate="G$1" x="285" y="73.74"/>
<instance part="COM6" gate="G$1" x="285" y="55.74"/>
<instance part="COM7" gate="G$1" x="285" y="37.74"/>
<instance part="COM8" gate="G$1" x="395" y="50"/>
<instance part="JP1A" gate="G$1" x="395" y="32"/>
<instance part="JP1B" gate="G$1" x="395" y="14"/>
<instance part="JP2A" gate="G$1" x="395" y="-4"/>
<instance part="JP2B" gate="G$1" x="395" y="-22"/>
<instance part="JP3A" gate="G$1" x="395" y="-40"/>
<instance part="JP3B" gate="G$1" x="395" y="-58"/>
<instance part="JP4A" gate="G$1" x="395" y="-76"/>
<instance part="JP4B" gate="G$1" x="395" y="-94"/>
<instance part="JP5A" gate="G$1" x="395" y="-112"/>
<instance part="JP5B" gate="G$1" x="395" y="-130"/>
<instance part="JP6A" gate="G$1" x="395" y="-148"/>
<instance part="JP6B" gate="G$1" x="395" y="-166"/>
<instance part="JP7A" gate="G$1" x="395" y="-184"/>
<instance part="JP7B" gate="G$1" x="395" y="-202"/>
</instances>
<busses>
</busses>
<nets>
<net name="3V3" class="0">
<segment><pinref part="U1" gate="G$1" pin="3V3"/><wire x1="57.46" y1="266" x2="52.38" y2="266" width="0.1524" layer="91"/><label x="52.38" y="266" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="VDD"/><wire x1="167.46" y1="266" x2="162.38" y2="266" width="0.1524" layer="91"/><label x="162.38" y="266" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U5" gate="G$1" pin="VCC"/><wire x1="167.46" y1="183.2" x2="162.38" y2="183.2" width="0.1524" layer="91"/><label x="162.38" y="183.2" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R4" gate="G$1" pin="1"/><wire x1="387.38" y1="212" x2="382.3" y2="212" width="0.1524" layer="91"/><label x="382.3" y="212" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J3" gate="G$1" pin="VDD"/><wire x1="167.46" y1="117.42" x2="162.38" y2="117.42" width="0.1524" layer="91"/><label x="162.38" y="117.42" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="TP1" gate="G$1" pin="3V3"/><wire x1="277.46" y1="266" x2="272.38" y2="266" width="0.1524" layer="91"/><label x="272.38" y="266" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP3A" gate="G$1" pin="1"/><wire x1="392.46" y1="-40" x2="387.38" y2="-40" width="0.1524" layer="91"/><label x="387.38" y="-40" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP3B" gate="G$1" pin="1"/><wire x1="392.46" y1="-58" x2="387.38" y2="-58" width="0.1524" layer="91"/><label x="387.38" y="-58" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP4A" gate="G$1" pin="1"/><wire x1="392.46" y1="-76" x2="387.38" y2="-76" width="0.1524" layer="91"/><label x="387.38" y="-76" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP4B" gate="G$1" pin="1"/><wire x1="392.46" y1="-94" x2="387.38" y2="-94" width="0.1524" layer="91"/><label x="387.38" y="-94" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="5V" class="0">
<segment><pinref part="U1" gate="G$1" pin="5V"/><wire x1="57.46" y1="220.28" x2="52.38" y2="220.28" width="0.1524" layer="91"/><label x="52.38" y="220.28" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J5" gate="G$1" pin="5V"/><wire x1="167.46" y1="72.72" x2="162.38" y2="72.72" width="0.1524" layer="91"/><label x="162.38" y="72.72" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U4" gate="G$1" pin="VCC"/><wire x1="167.46" y1="222.06" x2="162.38" y2="222.06" width="0.1524" layer="91"/><label x="162.38" y="222.06" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="C4" gate="G$1" pin="+"/><wire x1="387.38" y1="140" x2="382.3" y2="140" width="0.1524" layer="91"/><label x="382.3" y="140" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="TP1" gate="G$1" pin="5V"/><wire x1="277.46" y1="263.46" x2="272.38" y2="263.46" width="0.1524" layer="91"/><label x="272.38" y="263.46" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="GND" class="0">
<segment><pinref part="U1" gate="G$1" pin="GND@1"/><wire x1="57.46" y1="232.98" x2="52.38" y2="232.98" width="0.1524" layer="91"/><label x="52.38" y="232.98" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U1" gate="G$1" pin="GND@3"/><wire x1="85.4" y1="250.76" x2="90.48" y2="250.76" width="0.1524" layer="91"/><label x="90.48" y="250.76" size="1.778" layer="95"/></segment>
<segment><pinref part="U2" gate="G$1" pin="GND"/><wire x1="167.46" y1="263.46" x2="162.38" y2="263.46" width="0.1524" layer="91"/><label x="162.38" y="263.46" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="ADDR"/><wire x1="167.46" y1="255.84" x2="162.38" y2="255.84" width="0.1524" layer="91"/><label x="162.38" y="255.84" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="AIN3"/><wire x1="167.46" y1="243.14" x2="162.38" y2="243.14" width="0.1524" layer="91"/><label x="162.38" y="243.14" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U4" gate="G$1" pin="GND"/><wire x1="167.46" y1="224.6" x2="162.38" y2="224.6" width="0.1524" layer="91"/><label x="162.38" y="224.6" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U5" gate="G$1" pin="GND"/><wire x1="167.46" y1="180.66" x2="162.38" y2="180.66" width="0.1524" layer="91"/><label x="162.38" y="180.66" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J5" gate="G$1" pin="GND"/><wire x1="167.46" y1="70.18" x2="162.38" y2="70.18" width="0.1524" layer="91"/><label x="162.38" y="70.18" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J1" gate="G$1" pin="2"/><wire x1="167.46" y1="159.58" x2="162.38" y2="159.58" width="0.1524" layer="91"/><label x="162.38" y="159.58" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J4" gate="G$1" pin="2"/><wire x1="167.46" y1="91.26" x2="162.38" y2="91.26" width="0.1524" layer="91"/><label x="162.38" y="91.26" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J3" gate="G$1" pin="GND"/><wire x1="167.46" y1="112.34" x2="162.38" y2="112.34" width="0.1524" layer="91"/><label x="162.38" y="112.34" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R2" gate="G$1" pin="2"/><wire x1="402.62" y1="248" x2="407.7" y2="248" width="0.1524" layer="91"/><label x="407.7" y="248" size="1.778" layer="95"/></segment>
<segment><pinref part="R_SH1" gate="G$1" pin="1"/><wire x1="387.38" y1="194" x2="382.3" y2="194" width="0.1524" layer="91"/><label x="382.3" y="194" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R_SH2" gate="G$1" pin="2"/><wire x1="402.62" y1="176" x2="407.7" y2="176" width="0.1524" layer="91"/><label x="407.7" y="176" size="1.778" layer="95"/></segment>
<segment><pinref part="C1" gate="G$1" pin="2"/><wire x1="402.62" y1="158" x2="407.7" y2="158" width="0.1524" layer="91"/><label x="407.7" y="158" size="1.778" layer="95"/></segment>
<segment><pinref part="C4" gate="G$1" pin="-"/><wire x1="402.62" y1="140" x2="407.7" y2="140" width="0.1524" layer="91"/><label x="407.7" y="140" size="1.778" layer="95"/></segment>
<segment><pinref part="TP1" gate="G$1" pin="GND"/><wire x1="277.46" y1="260.92" x2="272.38" y2="260.92" width="0.1524" layer="91"/><label x="272.38" y="260.92" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP5A" gate="G$1" pin="1"/><wire x1="392.46" y1="-112" x2="387.38" y2="-112" width="0.1524" layer="91"/><label x="387.38" y="-112" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP5B" gate="G$1" pin="1"/><wire x1="392.46" y1="-130" x2="387.38" y2="-130" width="0.1524" layer="91"/><label x="387.38" y="-130" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP6A" gate="G$1" pin="1"/><wire x1="392.46" y1="-148" x2="387.38" y2="-148" width="0.1524" layer="91"/><label x="387.38" y="-148" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP6B" gate="G$1" pin="1"/><wire x1="392.46" y1="-166" x2="387.38" y2="-166" width="0.1524" layer="91"/><label x="387.38" y="-166" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP7A" gate="G$1" pin="1"/><wire x1="392.46" y1="-184" x2="387.38" y2="-184" width="0.1524" layer="91"/><label x="387.38" y="-184" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP7B" gate="G$1" pin="1"/><wire x1="392.46" y1="-202" x2="387.38" y2="-202" width="0.1524" layer="91"/><label x="387.38" y="-202" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="SDA" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO14"/><wire x1="57.46" y1="238.06" x2="52.38" y2="238.06" width="0.1524" layer="91"/><label x="52.38" y="238.06" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="SDA"/><wire x1="167.46" y1="258.38" x2="162.38" y2="258.38" width="0.1524" layer="91"/><label x="162.38" y="258.38" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U5" gate="G$1" pin="SDA"/><wire x1="167.46" y1="185.74" x2="162.38" y2="185.74" width="0.1524" layer="91"/><label x="162.38" y="185.74" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="SCL" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO27"/><wire x1="57.46" y1="240.6" x2="52.38" y2="240.6" width="0.1524" layer="91"/><label x="52.38" y="240.6" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="SCL"/><wire x1="167.46" y1="260.92" x2="162.38" y2="260.92" width="0.1524" layer="91"/><label x="162.38" y="260.92" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U5" gate="G$1" pin="SCL"/><wire x1="167.46" y1="188.28" x2="162.38" y2="188.28" width="0.1524" layer="91"/><label x="162.38" y="188.28" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP1A" gate="G$1" pin="1"/><wire x1="392.46" y1="32" x2="387.38" y2="32" width="0.1524" layer="91"/><label x="387.38" y="32" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP1B" gate="G$1" pin="1"/><wire x1="392.46" y1="14" x2="387.38" y2="14" width="0.1524" layer="91"/><label x="387.38" y="14" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="DQ" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO32"/><wire x1="57.46" y1="250.76" x2="52.38" y2="250.76" width="0.1524" layer="91"/><label x="52.38" y="250.76" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J3" gate="G$1" pin="DQ"/><wire x1="167.46" y1="114.88" x2="162.38" y2="114.88" width="0.1524" layer="91"/><label x="162.38" y="114.88" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R4" gate="G$1" pin="2"/><wire x1="402.62" y1="212" x2="407.7" y2="212" width="0.1524" layer="91"/><label x="407.7" y="212" size="1.778" layer="95"/></segment>
</net>
<net name="MISO" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO4"/><wire x1="85.4" y1="235.52" x2="90.48" y2="235.52" width="0.1524" layer="91"/><label x="90.48" y="235.52" size="1.778" layer="95"/></segment>
<segment><pinref part="U4" gate="G$1" pin="MISO"/><wire x1="167.46" y1="219.52" x2="162.38" y2="219.52" width="0.1524" layer="91"/><label x="162.38" y="219.52" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="MOSI" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO16"/><wire x1="85.4" y1="238.06" x2="90.48" y2="238.06" width="0.1524" layer="91"/><label x="90.48" y="238.06" size="1.778" layer="95"/></segment>
<segment><pinref part="U4" gate="G$1" pin="MOSI"/><wire x1="167.46" y1="216.98" x2="162.38" y2="216.98" width="0.1524" layer="91"/><label x="162.38" y="216.98" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="SCK" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO17"/><wire x1="85.4" y1="240.6" x2="90.48" y2="240.6" width="0.1524" layer="91"/><label x="90.48" y="240.6" size="1.778" layer="95"/></segment>
<segment><pinref part="U4" gate="G$1" pin="SCK"/><wire x1="167.46" y1="214.44" x2="162.38" y2="214.44" width="0.1524" layer="91"/><label x="162.38" y="214.44" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="CS" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO5"/><wire x1="85.4" y1="243.14" x2="90.48" y2="243.14" width="0.1524" layer="91"/><label x="90.48" y="243.14" size="1.778" layer="95"/></segment>
<segment><pinref part="U4" gate="G$1" pin="CS"/><wire x1="167.46" y1="211.9" x2="162.38" y2="211.9" width="0.1524" layer="91"/><label x="162.38" y="211.9" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN1" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO33"/><wire x1="57.46" y1="248.22" x2="52.38" y2="248.22" width="0.1524" layer="91"/><label x="52.38" y="248.22" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J2" gate="G$1" pin="IN1"/><wire x1="167.46" y1="141.04" x2="162.38" y2="141.04" width="0.1524" layer="91"/><label x="162.38" y="141.04" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN2" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO25"/><wire x1="57.46" y1="245.68" x2="52.38" y2="245.68" width="0.1524" layer="91"/><label x="52.38" y="245.68" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J2" gate="G$1" pin="IN2"/><wire x1="167.46" y1="138.5" x2="162.38" y2="138.5" width="0.1524" layer="91"/><label x="162.38" y="138.5" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN3" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO26"/><wire x1="57.46" y1="243.14" x2="52.38" y2="243.14" width="0.1524" layer="91"/><label x="52.38" y="243.14" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="J2" gate="G$1" pin="IN3"/><wire x1="167.46" y1="135.96" x2="162.38" y2="135.96" width="0.1524" layer="91"/><label x="162.38" y="135.96" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN4" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO23"/><wire x1="85.4" y1="263.46" x2="90.48" y2="263.46" width="0.1524" layer="91"/><label x="90.48" y="263.46" size="1.778" layer="95"/></segment>
<segment><pinref part="J6" gate="G$1" pin="IN4"/><wire x1="167.46" y1="51.64" x2="162.38" y2="51.64" width="0.1524" layer="91"/><label x="162.38" y="51.64" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN5" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO22"/><wire x1="85.4" y1="260.92" x2="90.48" y2="260.92" width="0.1524" layer="91"/><label x="90.48" y="260.92" size="1.778" layer="95"/></segment>
<segment><pinref part="J6" gate="G$1" pin="IN5"/><wire x1="167.46" y1="49.1" x2="162.38" y2="49.1" width="0.1524" layer="91"/><label x="162.38" y="49.1" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN6" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO21"/><wire x1="85.4" y1="253.3" x2="90.48" y2="253.3" width="0.1524" layer="91"/><label x="90.48" y="253.3" size="1.778" layer="95"/></segment>
<segment><pinref part="J6" gate="G$1" pin="IN6"/><wire x1="167.46" y1="46.56" x2="162.38" y2="46.56" width="0.1524" layer="91"/><label x="162.38" y="46.56" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN7" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO19"/><wire x1="85.4" y1="248.22" x2="90.48" y2="248.22" width="0.1524" layer="91"/><label x="90.48" y="248.22" size="1.778" layer="95"/></segment>
<segment><pinref part="J7" gate="G$1" pin="IN7"/><wire x1="167.46" y1="28.02" x2="162.38" y2="28.02" width="0.1524" layer="91"/><label x="162.38" y="28.02" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="IN8" class="0">
<segment><pinref part="U1" gate="G$1" pin="IO18"/><wire x1="85.4" y1="245.68" x2="90.48" y2="245.68" width="0.1524" layer="91"/><label x="90.48" y="245.68" size="1.778" layer="95"/></segment>
<segment><pinref part="J7" gate="G$1" pin="IN8"/><wire x1="167.46" y1="25.48" x2="162.38" y2="25.48" width="0.1524" layer="91"/><label x="162.38" y="25.48" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="PV" class="0">
<segment><pinref part="J1" gate="G$1" pin="1"/><wire x1="167.46" y1="162.12" x2="162.38" y2="162.12" width="0.1524" layer="91"/><label x="162.38" y="162.12" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R1" gate="G$1" pin="1"/><wire x1="387.38" y1="266" x2="382.3" y2="266" width="0.1524" layer="91"/><label x="382.3" y="266" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM1" gate="G$1" pin="1"/><wire x1="392.46" y1="122" x2="387.38" y2="122" width="0.1524" layer="91"/><label x="387.38" y="122" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM2" gate="G$1" pin="1"/><wire x1="392.46" y1="104" x2="387.38" y2="104" width="0.1524" layer="91"/><label x="387.38" y="104" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM3" gate="G$1" pin="1"/><wire x1="392.46" y1="86" x2="387.38" y2="86" width="0.1524" layer="91"/><label x="387.38" y="86" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM4" gate="G$1" pin="1"/><wire x1="392.46" y1="68" x2="387.38" y2="68" width="0.1524" layer="91"/><label x="387.38" y="68" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM5" gate="G$1" pin="1"/><wire x1="282.46" y1="73.74" x2="277.38" y2="73.74" width="0.1524" layer="91"/><label x="277.38" y="73.74" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM6" gate="G$1" pin="1"/><wire x1="282.46" y1="55.74" x2="277.38" y2="55.74" width="0.1524" layer="91"/><label x="277.38" y="55.74" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM7" gate="G$1" pin="1"/><wire x1="282.46" y1="37.74" x2="277.38" y2="37.74" width="0.1524" layer="91"/><label x="277.38" y="37.74" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="COM8" gate="G$1" pin="1"/><wire x1="392.46" y1="50" x2="387.38" y2="50" width="0.1524" layer="91"/><label x="387.38" y="50" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="DIV" class="0">
<segment><pinref part="R1" gate="G$1" pin="2"/><wire x1="402.62" y1="266" x2="407.7" y2="266" width="0.1524" layer="91"/><label x="407.7" y="266" size="1.778" layer="95"/></segment>
<segment><pinref part="R2" gate="G$1" pin="1"/><wire x1="387.38" y1="248" x2="382.3" y2="248" width="0.1524" layer="91"/><label x="382.3" y="248" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R3" gate="G$1" pin="1"/><wire x1="387.38" y1="230" x2="382.3" y2="230" width="0.1524" layer="91"/><label x="382.3" y="230" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="A0" class="0">
<segment><pinref part="R3" gate="G$1" pin="2"/><wire x1="402.62" y1="230" x2="407.7" y2="230" width="0.1524" layer="91"/><label x="407.7" y="230" size="1.778" layer="95"/></segment>
<segment><pinref part="C1" gate="G$1" pin="1"/><wire x1="387.38" y1="158" x2="382.3" y2="158" width="0.1524" layer="91"/><label x="382.3" y="158" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="AIN0"/><wire x1="167.46" y1="250.76" x2="162.38" y2="250.76" width="0.1524" layer="91"/><label x="162.38" y="250.76" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="REF" class="0">
<segment><pinref part="J4" gate="G$1" pin="1"/><wire x1="167.46" y1="93.8" x2="162.38" y2="93.8" width="0.1524" layer="91"/><label x="162.38" y="93.8" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R_SH2" gate="G$1" pin="1"/><wire x1="387.38" y1="176" x2="382.3" y2="176" width="0.1524" layer="91"/><label x="382.3" y="176" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="U2" gate="G$1" pin="AIN1"/><wire x1="167.46" y1="248.22" x2="162.38" y2="248.22" width="0.1524" layer="91"/><label x="162.38" y="248.22" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="LB" class="0">
<segment><pinref part="U2" gate="G$1" pin="AIN2"/><wire x1="167.46" y1="245.68" x2="162.38" y2="245.68" width="0.1524" layer="91"/><label x="162.38" y="245.68" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="R_SH1" gate="G$1" pin="2"/><wire x1="402.62" y1="194" x2="407.7" y2="194" width="0.1524" layer="91"/><label x="407.7" y="194" size="1.778" layer="95"/></segment>
<segment><pinref part="RL1" gate="G$1" pin="2"/><wire x1="277.46" y1="239.84" x2="272.38" y2="239.84" width="0.1524" layer="91"/><label x="272.38" y="239.84" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL2" gate="G$1" pin="2"/><wire x1="277.46" y1="218.76" x2="272.38" y2="218.76" width="0.1524" layer="91"/><label x="272.38" y="218.76" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL3" gate="G$1" pin="2"/><wire x1="277.46" y1="197.68" x2="272.38" y2="197.68" width="0.1524" layer="91"/><label x="272.38" y="197.68" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL4" gate="G$1" pin="2"/><wire x1="277.46" y1="176.6" x2="272.38" y2="176.6" width="0.1524" layer="91"/><label x="272.38" y="176.6" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL5" gate="G$1" pin="2"/><wire x1="277.46" y1="155.52" x2="272.38" y2="155.52" width="0.1524" layer="91"/><label x="272.38" y="155.52" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL6" gate="G$1" pin="2"/><wire x1="277.46" y1="134.44" x2="272.38" y2="134.44" width="0.1524" layer="91"/><label x="272.38" y="134.44" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL7" gate="G$1" pin="2"/><wire x1="277.46" y1="113.36" x2="272.38" y2="113.36" width="0.1524" layer="91"/><label x="272.38" y="113.36" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="RL8" gate="G$1" pin="2"/><wire x1="277.46" y1="92.28" x2="272.38" y2="92.28" width="0.1524" layer="91"/><label x="272.38" y="92.28" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP2A" gate="G$1" pin="1"/><wire x1="392.46" y1="-4" x2="387.38" y2="-4" width="0.1524" layer="91"/><label x="387.38" y="-4" size="1.778" layer="95" rot="R180"/></segment>
<segment><pinref part="JP2B" gate="G$1" pin="1"/><wire x1="392.46" y1="-22" x2="387.38" y2="-22" width="0.1524" layer="91"/><label x="387.38" y="-22" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO1" class="0">
<segment><pinref part="RL1" gate="G$1" pin="1"/><wire x1="277.46" y1="242.38" x2="272.38" y2="242.38" width="0.1524" layer="91"/><label x="272.38" y="242.38" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO2" class="0">
<segment><pinref part="RL2" gate="G$1" pin="1"/><wire x1="277.46" y1="221.3" x2="272.38" y2="221.3" width="0.1524" layer="91"/><label x="272.38" y="221.3" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO3" class="0">
<segment><pinref part="RL3" gate="G$1" pin="1"/><wire x1="277.46" y1="200.22" x2="272.38" y2="200.22" width="0.1524" layer="91"/><label x="272.38" y="200.22" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO4" class="0">
<segment><pinref part="RL4" gate="G$1" pin="1"/><wire x1="277.46" y1="179.14" x2="272.38" y2="179.14" width="0.1524" layer="91"/><label x="272.38" y="179.14" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO5" class="0">
<segment><pinref part="RL5" gate="G$1" pin="1"/><wire x1="277.46" y1="158.06" x2="272.38" y2="158.06" width="0.1524" layer="91"/><label x="272.38" y="158.06" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO6" class="0">
<segment><pinref part="RL6" gate="G$1" pin="1"/><wire x1="277.46" y1="136.98" x2="272.38" y2="136.98" width="0.1524" layer="91"/><label x="272.38" y="136.98" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO7" class="0">
<segment><pinref part="RL7" gate="G$1" pin="1"/><wire x1="277.46" y1="115.9" x2="272.38" y2="115.9" width="0.1524" layer="91"/><label x="272.38" y="115.9" size="1.778" layer="95" rot="R180"/></segment>
</net>
<net name="NO8" class="0">
<segment><pinref part="RL8" gate="G$1" pin="1"/><wire x1="277.46" y1="94.82" x2="272.38" y2="94.82" width="0.1524" layer="91"/><label x="272.38" y="94.82" size="1.778" layer="95" rot="R180"/></segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
</eagle>
