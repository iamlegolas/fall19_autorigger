all = []

head_f = [u'Fan_Geo.f[1185:1237]',
 u'Fan_Geo.f[1256:1330]',
 u'Fan_Geo.f[2067:2160]',
 u'Fan_Geo.f[1238:1255]']
all += head_f

poncho_f = [u'Fan_Geo.f[4523:4546]',
 u'Fan_Geo.f[4673:4675]',
 u'Fan_Geo.f[4680:4686]',
 u'Fan_Geo.f[4690:4692]',
 u'Fan_Geo.f[4701:4730]',
 u'Fan_Geo.f[4737:4739]',
 u'Fan_Geo.f[4743:4744]',
 u'Fan_Geo.f[4905:4921]',
 u'Fan_Geo.f[4947:5321]',
 u'Fan_Geo.f[6293:6344]']
poncho_collar_f = [u'Fan_Geo.f[4839:4904]',
 u'Fan_Geo.f[6279:6292]']
poncho_acsr_01_f = [u'Fan_Geo.f[4745:4757]',
 u'Fan_Geo.f[4830:4832]']
poncho_acsr_02_f = [u'Fan_Geo.f[4676:4679]',
 u'Fan_Geo.f[4687:4689]',
 u'Fan_Geo.f[4693:4700]',
 u'Fan_Geo.f[4731:4736]',
 u'Fan_Geo.f[4740:4742]']
poncho = poncho_f + poncho_collar_f + poncho_acsr_01_f + poncho_acsr_02_f
all += poncho_f + poncho_collar_f + poncho_acsr_01_f + poncho_acsr_02_f

braid_f = [u'Fan_Geo.f[1331:2066]']
braid_end_f = [u'Fan_Geo.f[2161:2448]']
braid_acsr_f = [u'Fan_Geo.f[2449:2548]']
braid = braid_f + braid_end_f + braid_acsr_f
all += braid_f + braid_end_f + braid_acsr_f

skirt_f = [u'Fan_Geo.f[0:211]',
 u'Fan_Geo.f[1120:1184]',
 u'Fan_Geo.f[6345:6376]',
 u'Fan_Geo.f[7478:7605]']
skirt_acsr_01_f = [u'Fan_Geo.f[1026:1119]']
skirt_acsr_02_f = [u'Fan_Geo.f[918:1025]']
skirt = skirt_f + skirt_acsr_01_f + skirt_acsr_02_f
all += skirt_f + skirt_acsr_01_f + skirt_acsr_02_f

sleeves_f = [u'Fan_Geo.f[6377:6481]',
 u'Fan_Geo.f[7051:7421]']
all += sleeves_f

earring_l = [u'Fan_Geo.f[4758:4793]',
 u'Fan_Geo.f[4833:4838]']
earring_r = [u'Fan_Geo.f[4547:4552]',
 u'Fan_Geo.f[4794:4829]']
all += earring_l + earring_r


cmds.showHidden(all)
cmds.hide(all)

cmds.hide(sleeves_f)
cmds.showHidden(sleeves_f)
cmds.hide(poncho)
cmds.showHidden(poncho)

cmds.ls(sl=1)
cmds.select(skirt)