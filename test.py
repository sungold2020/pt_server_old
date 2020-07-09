#!/usr/bin/python3
import re

SummaryStr='''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="NexusPHP" />
<title>JoyHD :: 种子详情 &quot;Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD&quot; 看得见的精彩 - Powered by NexusPHP</title>
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
<link rel="search" type="application/opensearchdescription+xml" title="JoyHD Torrents" href="opensearch.php" />
<link rel="stylesheet" href="styles/mediumfont.css?201312010030" type="text/css" />
<link rel="stylesheet" href="pic/forum_pic/chs/forumsprites.css?201312010030" type="text/css" />
<link rel="stylesheet" href="styles/BlueGene/theme.css?201312010030" type="text/css" />
<link rel="stylesheet" href="styles/BlueGene/DomTT.css?201312010030" type="text/css" />

<link rel="stylesheet" href="/minify/?f=styles/sprites.css,jquerylib/jquery.alerts.css,styles/curtain_imageresizer.css&20190105" type="text/css" />
<link rel="stylesheet" href="pic/category/chd/scenetorrents/catsprites.css?201312010030" type="text/css" />
<link rel="alternate" type="application/rss+xml" title="Latest Torrents" href="torrentrss.php" />

<script type="text/javascript" src="/minify/?f=curtain_imageresizer.js,ajaxbasic.js,common.js,domLib.js,domTT.js,domTT_drag.js,fadomatic.js,jquerylib/jquery-1.5.2.min.js,jquerylib/jquery.alerts.js,jquerylib/jquery.ui.draggable.js,jquerylib/jquery.caretInsert.js,userAutoTips.js,js/jquery.SuperSlide.2.1.1.js&20190105" </script>
<link href="css/style.css" rel="stylesheet" type="text/css">
<link rel="stylesheet" href="userAutoTips.css" type="text/css">

</head>
<body>
<script>
 
/* 点击按钮，返回顶部
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}*/
</script>

<script type="text/javascript">
$(document).ready(function(){
        $('#roll_top').click(function(){$('html,body').animate({scrollTop: '0px'}, 800);});
	$('#roll_bottom').click(function(){$('html,body').animate({scrollTop:$('#footer').offset().top}, 800);});
	t_ids = $('textarea');
	if(t_ids)
	{
		for(var i = 0 ;i <t_ids.length;i++)
		{
			userAutoTips({id:t_ids[i].id});
		}
	}
        $('#roll_top').click(function(){$('html,body').animate({scrollTop: '0px'}, 800);});
	$('#roll_bottom').click(function(){$('html,body').animate({scrollTop:$('#footer').offset().top}, 800);});
});

</script>
<script type="text/javascript">
$(".prev,.next").hover(function(){
	$(this).stop(true,false).fadeTo("show",0.9);
},function(){
	$(this).stop(true,false).fadeTo("show",0.4);
})

$(".mtime-box").slide({
	titCell:".hd ul",
	mainCell:".bd ul",
	effect:"fold",
	interTime:3500,
	delayTime:500,
	autoPlay:true,
	autoPage:true, 
	trigger:"click" 
});
</script>
<style type="text/css">
html body {
_background-image:url(about:blank);
_background-attachment:fixed;
}
#roll_top,#roll_bottom {
    position:relative;
    cursor:pointer;
    height:52px;
    width:50px;
    }
#roll_top {
    background:url(pic/top.png) no-repeat;
    }
#roll_bottom {
    background:url(pic/up.png) no-repeat 0 -52px;
    display: none;
    }
#roll {
    display:block;
    width:50px;
    margin-right:-546px;  /*这个是距离的位置，请自行调整*/
    position:fixed;
    right:50%;
    top:90%;
    _margin-right:-545px;/*Hack IE6的，请用IE6打开自行调整*/
    _position:absolute;
    _margin-top:300px;
    _top:expression(eval(document.documentElement.scrollTop));
    }
</style>

<div id="roll"><div title="回到顶部" onclick="topFunction()" id="roll_top"></div><div title="转到底部" id="roll_bottom"></div></div>





		<table class="head" cellspacing="0" cellpadding="0" align="center">
<tr>
		<td class="clear">
			<div class="logo_img"><img src="/banner/logo-201608.png" alt="JoyHD" title="JoyHD - 只想安安静静的看电影" /></div>
		<td class="clear nowrap" align="right" valign="middle">
		
			<a href="donate.php"><img src="pic/forum_pic/chs/donate.gif" alt="Make a donation" style="margin-left: 5px; margin-top: 50px;" /></a>
		</td>
	</tr></table><table class="mainouter" width="982" cellspacing="0" cellpadding="5" align="center">
	


	<tr><td id="nav_block" class="text" align="center">
<table class="main" width="940" border="0" cellspacing="0" cellpadding="0"><tr><td class="embedded" ><script type="text/javascript">
function showHideDIV(){
var doc = document.getElementById("shoutboxContainer");
doc.style.display =
(doc.style.display == "none"?"block":"none");
}
</script>


<div id="nav"><ul id="mainmenu" class="menu"><li><a href="index.php">&nbsp;首&nbsp;&nbsp;页&nbsp;</a></li><li><a href="forums.php">&nbsp;论&nbsp;&nbsp;坛&nbsp;</a></li><li><a href="torrents.php">&nbsp;种&nbsp;&nbsp;子&nbsp;</a></li><li><a href="upload.php">&nbsp;发&nbsp;&nbsp;布&nbsp;</a></li><li><a href="subtitles.php">&nbsp;字&nbsp;&nbsp;幕&nbsp;</a></li><li><a href="recycle.php">&nbsp;候选区&nbsp;</a></li><li><a href="usercp.php">&nbsp;个人信息&nbsp;</a></li><li><a href="topten.php">排&nbsp;行&nbsp;榜</a></li><li><a href="log.php">&nbsp;日&nbsp;&nbsp;志&nbsp;</a></li><li><a href="rules.php">&nbsp;规&nbsp;&nbsp;则&nbsp;</a></li><li><a href="faq.php">&nbsp;常见问题&nbsp;</a></li></ul></div></td></tr></table>









<table id="info_block" cellpadding="4" cellspacing="0" border="0" width="100%"><tr>
	<td><table width="100%" cellspacing="0" cellpadding="0" border="0"><tr>
		<td class="bottom" align="left"><span class="medium">欢迎回家, <span class="nowrap"><a  href="userdetails.php?id=18394" class='CrazyUser_Name'><b>sungold</b></a></span>  [<a href="logout.php">退出</a>]   [<a href="torrents.php?inclbookmarked=1&amp;allsec=1&amp;incldead=0">收藏</a>] <font class = 'color_bonus'>银元 </font>[<a href="mybonus.php">使用</a>丨<a href="usebonus.php">游戏</a>]: 52,551 <font class = 'color_invite'>邀请 </font>[<a href="invite.php?id=18394">发送</a>]: 5<br />

	<font class="color_ratio">分享率：</font> 2.858	<font class='color_uploaded'>上传量：</font> 1.003 TB	<font class='color_downloaded'> 下载量：</font> 359.54 GB	<font class='color_active'>当前活动：</font>
	<a href="userdetails.php?id=18394&show=seeding"><img class="arrowup" alt="Torrents seeding" title="当前做种"  src="pic/trans.gif" />1</a>
	<a href="userdetails.php?id=18394&show=leeching"><img class="arrowdown" alt="Torrents leeching" title="当前下载" src="pic/trans.gif" />0</a>
	<!--
	<a href="userdetails.php?id=18394&show=completed" title="已完成"><img class="completed" alt="completed" title="已完成"  src="pic/trans.gif" />--</a>
	<a href="userdetails.php?id=18394&show=uploaded" title="已发布"><img class="uploaded" alt="uploaded" title="已发布"  src="pic/trans.gif" />--</a>
	-->

	<font class='color_connectable'>可连接：</font><b><font color="green">是</font></b> </span></td>

	<td class="bottom" align="right"><span class="medium">当前时间：12:33<br />

<a href="messages.php"><img class="inbox" src="pic/trans.gif" alt="inbox" title="收件箱&nbsp;(无新消息)" /></a> 0  <a href="messages.php?action=viewmailbox&amp;box=-1"><img class="sentbox" alt="sentbox" title="发件箱" src="pic/trans.gif" /></a> 0 <a href="friends.php"><img class="buddylist" alt="Buddylist" title="好友列表" src="pic/trans.gif" /></a> <a href="getrss.php"><img class="rss" alt="RSS" title="获取RSS" src="pic/trans.gif" /></a>
﻿<form name="form1" enctype="multipart/form-data" method="post" action="changelanguage.php"> 
<label> 
<select name="select"> 
<option value="0">Language</option> 
<option value="6">English</option> 
<option value="25">简体中文</option> 
<option value="28">繁體中文</option> 

</select> 
</label> 
<label> 
<input type="submit" name="Submit" value="Go"> 
</label> 
</form>

	</span></td>
	</tr></table></td>
</tr></table>
</div>
    </div>
</td></tr>

<tr><td id="outer" align="center" class="outer" style="padding-top: 20px; padding-bottom: 20px">
<h1 align="center" id="top">Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD</h1>
<table width="940" cellspacing="0" cellpadding="5">
<tr><td class="rowhead" width="13%">下载</td><td class="rowfollow" width="87%" align="left"><a class="index" href="download.php?id=71945">[JoyHD].Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD.torrent</a>&nbsp;&nbsp;&nbsp;由&nbsp;<span class="nowrap"><b>管理员可见</b></span>发布于<span title="2020-07-03 06:09:29">1天6时前</span></td></tr><tr><td class="rowhead" width="13%">下载方式</td><td class="rowfollow" width="87%" align="left"><font color=brown>提示：请尽量保种，感谢你对JoyHD的支持。请使用稳定版下载客户端不要随意升级。</td></tr><tr><td class="rowhead nowrap" valign="top" align="right">副标题</td><td class="rowfollow" valign="top" align="left">愤怒的黄牛 / Unstoppable / 愤怒的公牛 / 非卖品(台)</td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">基本信息</td><td class="rowfollow" valign="top" align="left"><b><b>大小：</b></b>7.48 GB&nbsp;&nbsp;&nbsp;<b>类型:</b>&nbsp;Movie&nbsp;&nbsp;&nbsp;<b>子类型:&nbsp;</b>电影-1080P&nbsp;&nbsp;&nbsp;<b>媒介:&nbsp;</b>Blu-ray&nbsp;&nbsp;&nbsp;<b>编码:&nbsp;</b>H.265&nbsp;&nbsp;&nbsp;<b>音频编码:&nbsp;</b>TrueHD&nbsp;&nbsp;&nbsp;<b>分辨率:&nbsp;</b>1080p&nbsp;&nbsp;&nbsp;<b>处理:&nbsp;</b>Encode&nbsp;&nbsp;&nbsp;<b>制作组:&nbsp;</b>JoyHD</td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">行为</td><td class="rowfollow" valign="top" align="left"><a title="下载种子" href="download.php?id=71945"><img class="dt_download" src="pic/trans.gif" alt="download" />&nbsp;<b><font class="small">下载种子</font></b></a>&nbsp;|&nbsp;<a id="bookmark71945"  href="javascript: bookmark(71945,71945);" ><b><font class="small">收藏<img class="delbookmark" src="pic/trans.gif" alt="Unbookmarked" title="收藏" /></font></b></a>&nbsp;|&nbsp;<a title="举报该种子违反了规则" href="report.php?torrent=71945"><img class="dt_report" src="pic/trans.gif" alt="report" />&nbsp;<b><font class="small">举报种子</font></b></a></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">直接下载链接</td><td class="rowfollow" valign="top" align="left"> <input type="text" id="text_download" readonly="readonly"  value="https://www.joyhd.net/download.php?id=71945&passkey=a770594966a29653632f94dce676f3b8" style="width: 291px" onmouseover="this.select()" /><a href="https://www.joyhd.net/download.php?id=71945&passkey=a770594966a29653632f94dce676f3b8" target="blank">&nbsp;</a></td></tr>
<tr><td class="rowhead" valign="top">字幕</td><td class="rowfollow" align="left" valign="top"><table border="0" cellspacing="0"><tr><td class="embedded">该种子暂无字幕</td></tr></table><table border="0" cellspacing="0"><tr><td class="embedded"><form method="post" action="subtitles.php"><input type="hidden" name="torrent_name" value="Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD" /><input type="hidden" name="detail_torrent_id" value="71945" /><input type="hidden" name="in_detail" value="in_detail" /><input type="submit" value="上传字幕" /></form></td><td class="embedded"><form method="get" action="https://zimuku.cn/search" target="_blank"><input type="text" name="q" id="keyword" style="width: 250px" value="" /><input type="submit" value="搜索字幕库" /></form></td><td class="embedded"><td class="embedded"><form method="get" action="http://www.opensubtitles.org/zh/search/" target="_blank"><input type="hidden" id="moviename" name="MovieName" /><input type="hidden" name="action" value="search" /><input type="hidden" name="SubLanguageID" value="all" /><input onclick="document.getElementById('moviename').value=document.getElementById('keyword').value;" type="submit" value="搜索Opensubtitles" /></form></td>
</tr></table></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right"><a href="javascript: klappe_news('descr')"><span class="nowrap"><img class="minus" src="pic/trans.gif" alt="Show/Hide" id="picdescr" title="" /> 简介</span></a><br /><font color=#999999>[点击图片可放大]</font></td><td class="rowfollow" valign="top" align="left"><div id='kdescr'><img id="attach10367" alt="Cover.jpg" src="attachments/202007/20200703060519d0bee21ca58c2a98b61bf4eaa7048b1e.jpg.thumb.jpg" onclick="Previewurl('attachments/202007/20200703060519d0bee21ca58c2a98b61bf4eaa7048b1e.jpg')" onmouseover="domTT_activate(this, event, 'content', '&lt;strong&gt;大小&lt;/strong&gt;: 378.75 KB&lt;br /&gt;&lt;span title=&quot;2020-07-03 06:05:19&quot;&gt;1天6时前&lt;/span&gt;', 'styleClass', 'attach', 'x', findPosition(this)[0], 'y', findPosition(this)[1]-58);" /><br />
<br />
◎译　　名　愤怒的黄牛 / Unstoppable / 愤怒的公牛 / 非卖品(台)<br />
◎片　　名　성난황소<br />
◎年　　代　2018<br />
◎产　　地　韩国<br />
◎类　　别　动作 / 犯罪<br />
◎语　　言　韩语<br />
◎上映日期　2018-11-22(韩国)<br />
◎IMDb评分 &nbsp;6.6/10 from 1206 users<br />
◎IMDb链接 &nbsp;<a class="faqlink" href="https://www.imdb.com/title/tt9225192">https://www.imdb.com/title/tt9225192</a><br />
◎豆瓣评分　6.4/10 from 19260 users<br />
◎豆瓣链接　<a class="faqlink" href="https://movie.douban.com/subject/30181789/">https://movie.douban.com/subject/30181789/</a><br />
◎片　　长　115分钟<br />
◎导　　演　金旻昊 Kim Min-Ho<br />
◎编　　剧　金旻昊 Kim Min-Ho<br />
◎主　　演　马东锡 Tong-Seok Ma<br />
　　　　　 &nbsp;宋智孝 Ji-hyo Song<br />
　　　　　 &nbsp;金圣武 Seong-oh Kim<br />
　　　　　 &nbsp;金敏载 Kim Min-jae<br />
　　　　　 &nbsp;朴智焕 Park Ji-hwan<br />
<br />
<br />
◎标　　签　韩国 | 动作 | 犯罪 | 暴力 | 动作/犯罪/警匪 | 剧情 | 人性 | 贩卖妇女<br />
<br />
◎简　　介 &nbsp;<br />
<br />
　　该片讲述妻子被恶党绑架，丈夫与帮手一起赤手空拳地摧垮了绑架团伙，拯救妻子的故事。<br />
<br />
<img id="attach9305" alt="info.png" src="attachments/201808/20180818204606fe11bfeb1c7ce484c5efc18efe478bd3.png" onclick="Previewurl('attachments/201808/20180818204606fe11bfeb1c7ce484c5efc18efe478bd3.png')" onmouseover="domTT_activate(this, event, 'content', '&lt;strong&gt;大小&lt;/strong&gt;: 12.99 KB&lt;br /&gt;&lt;span title=&quot;2018-08-18 20:46:06&quot;&gt;1年10月前&lt;/span&gt;', 'styleClass', 'attach', 'x', findPosition(this)[0], 'y', findPosition(this)[1]-58);" /><br />
<br /><div class="codetop">代码</div><div class="codemain"><br />
General<br />
Unique ID                      : 335290017359941736692568502810158459857 (0xFC3E8229B2B7E3851C725F80209E6BD1)<br />
Complete name                  : Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD.mkv<br />
Format                         : Matroska<br />
Format version                 : Version 4<br />
File size                      : 7.43 GiB<br />
Duration                       : 1 h 56 min<br />
Overall bit rate mode          : Variable<br />
Overall bit rate               : 9 163 kb/s<br />
Encoded date                   : UTC 2020-07-02 14:27:51<br />
Writing application            : mkvmerge v37.0.0 ('Leave It') 64-bit<br />
Writing library                : libebml v1.3.9 + libmatroska v1.5.2<br />
<br />
Video<br />
ID                             : 1<br />
Format                         : HEVC<br />
Format/Info                    : High Efficiency Video Coding<br />
Format profile                 : Main@L4@Main<br />
Codec ID                       : V_MPEGH/ISO/HEVC<br />
Duration                       : 1 h 56 min<br />
Bit rate                       : 8 055 kb/s<br />
Width                          : 1 920 pixels<br />
Height                         : 804 pixels<br />
Display aspect ratio           : 2.40:1<br />
Frame rate mode                : Constant<br />
Frame rate                     : 23.976 (24000/1001) FPS<br />
Original frame rate            : 23.976 (23976/1000) FPS<br />
Color space                    : YUV<br />
Chroma subsampling             : 4:2:0<br />
Bit depth                      : 8 bits<br />
Bits/(Pixel*Frame)             : 0.218<br />
Stream size                    : 6.53 GiB (88%)<br />
Writing library                : x265 2.2+2-998d4520d1cf:[Windows][GCC 6.2.0][64 bit] 8bit+10bit+12bit<br />
Language                       : Korean<br />
Default                        : Yes<br />
Forced                         : No<br />
yuv  [info]: 1920x804 fps 23976/1000 i420p8 unknown frame count<br />
x265 [info]: HEVC encoder version 2.2+2-998d4520d1cf<br />
x265 [info]: build info [Windows][GCC 6.2.0][64 bit] 8bit+10bit+12bit<br />
x265 [info]: using cpu capabilities: MMX2 SSE2Fast LZCNT<br />
x265 [info]: Main profile, Level-4 (Main tier)<br />
x265 [info]: Thread pool created using 6 threads<br />
x265 [info]: Slices                              : 1<br />
x265 [info]: frame threads / pool features       : 8 / wpp(13 rows)<br />
x265 [info]: Coding QT: max CU size, min CU size : 64 / 16<br />
x265 [info]: Residual QT: max TU size, max depth : 32 / 1 inter / 1 intra<br />
x265 [info]: ME / range / subpel / merge         : star / 57 / 0 / 2<br />
x265 [info]: Keyframe min / max / scenecut / bias: 23 / 250 / 0 / 5.00<br />
x265 [info]: Lookahead / bframes / badapt        : 5 / 3 / 0<br />
x265 [info]: b-pyramid / weightp / weightb       : 1 / 0 / 0<br />
x265 [info]: References / ref-limit  cu / depth  : 1 / off / off<br />
x265 [info]: AQ: mode / str / qg-size / cu-tree  : 1 / 0.0 / 32 / 1<br />
x265 [info]: Rate Control / qCompress            : ABR-8000 kbps / 0.60<br />
x265 [info]: tools: rd=2 psy-rd=2.00 early-skip rskip tmvp fast-intra<br />
x265 [info]: tools: strong-intra-smoothing lslices=5 deblock<br />
x265 [info]: frame I:    668, Avg QP:13.49  kb/s: 32792.61<br />
x265 [info]: frame P:  42215, Avg QP:15.42  kb/s: 15898.10<br />
x265 [info]: frame B: 124086, Avg QP:17.92  kb/s: 5236.86 <br />
<br />
Audio<br />
ID                             : 2<br />
Format                         : MLP FBA<br />
Format/Info                    : Meridian Lossless Packing FBA<br />
Commercial name                : Dolby TrueHD<br />
Codec ID                       : A_TRUEHD<br />
Duration                       : 1 h 56 min<br />
Bit rate mode                  : Variable<br />
Bit rate                       : 1 025 kb/s<br />
Maximum bit rate               : 2 562 kb/s<br />
Channel(s)                     : 6 channels<br />
Channel layout                 : L R C LFE Ls Rs<br />
Sampling rate                  : 48.0 kHz<br />
Frame rate                     : 1 200.000 FPS (40 SPF)<br />
Compression mode               : Lossless<br />
Stream size                    : 851 MiB (11%)<br />
Language                       : Korean<br />
Default                        : Yes<br />
Forced                         : No<br />
<br />
Text #1<br />
ID                             : 3<br />
Format                         : PGS<br />
Muxing mode                    : zlib<br />
Codec ID                       : S_HDMV/PGS<br />
Codec ID/Info                  : Picture based subtitle format used on BDs/HD-DVDs<br />
Duration                       : 1 h 52 min<br />
Bit rate                       : 21.4 kb/s<br />
Count of elements              : 2922<br />
Stream size                    : 17.3 MiB (0%)<br />
Language                       : Chinese<br />
Default                        : Yes<br />
Forced                         : No<br />
<br />
Text #2<br />
ID                             : 4<br />
Format                         : PGS<br />
Muxing mode                    : zlib<br />
Codec ID                       : S_HDMV/PGS<br />
Codec ID/Info                  : Picture based subtitle format used on BDs/HD-DVDs<br />
Duration                       : 1 h 52 min<br />
Bit rate                       : 22.2 kb/s<br />
Count of elements              : 2922<br />
Stream size                    : 17.9 MiB (0%)<br />
Language                       : Chinese<br />
Default                        : No<br />
Forced                         : No<br />
</div><br /><br />
<br />
<img id="attach9306" alt="screen.png" src="attachments/201808/20180818204617b81803ac0903724ad88de90649c5a36e.png" onclick="Previewurl('attachments/201808/20180818204617b81803ac0903724ad88de90649c5a36e.png')" onmouseover="domTT_activate(this, event, 'content', '&lt;strong&gt;大小&lt;/strong&gt;: 15.43 KB&lt;br /&gt;&lt;span title=&quot;2018-08-18 20:46:17&quot;&gt;1年10月前&lt;/span&gt;', 'styleClass', 'attach', 'x', findPosition(this)[0], 'y', findPosition(this)[1]-58);" /><br />
<img id="attach10368" alt="Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD.jpg" src="attachments/202007/20200703060616c24d68c727b8fb810dcb9a1915b71758.jpg.thumb.jpg" onclick="Previewurl('attachments/202007/20200703060616c24d68c727b8fb810dcb9a1915b71758.jpg')" onmouseover="domTT_activate(this, event, 'content', '&lt;strong&gt;大小&lt;/strong&gt;: 382.44 KB&lt;br /&gt;&lt;span title=&quot;2020-07-03 06:06:16&quot;&gt;1天6时前&lt;/span&gt;', 'styleClass', 'attach', 'x', findPosition(this)[0], 'y', findPosition(this)[1]-58);" /><br />
</div></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right"><a href="javascript: klappe_news('nfo')"><img class="plus" src="pic/trans.gif" alt="Show/Hide" id="picnfo" title="" /> NFO</a><br /><a href="viewnfo.php?id=71945" class="sublink">[所有模式]</a></td><td class="rowfollow" valign="top" align="left"><div id='knfo' style="display: none;"><pre style="font-size:10pt; font-family: 'Courier New', monospace;">General
Unique ID                      : 335290017359941736692568502810158459857 (0xFC3E8229B2B7E3851C725F80209E6BD1)
Complete name                  : Unstoppable JPN 2018 Bluray 1080p HEVC TrueHD 5.1-JoyHD.mkv
Format                         : Matroska
Format version                 : Version 4
File size                      : 7.43 GiB
Duration                       : 1 h 56 min
Overall bit rate mode          : Variable
Overall bit rate               : 9 163 kb/s
Encoded date                   : UTC 2020-07-02 14:27:51
Writing application            : mkvmerge v37.0.0 ('Leave It') 64-bit
Writing library                : libebml v1.3.9 + libmatroska v1.5.2

Video
ID                             : 1
Format                         : HEVC
Format/Info                    : High Efficiency Video Coding
Format profile                 : Main@L4@Main
Codec ID                       : V_MPEGH/ISO/HEVC
Duration                       : 1 h 56 min
Bit rate                       : 8 055 kb/s
Width                          : 1 920 pixels
Height                         : 804 pixels
Display aspect ratio           : 2.40:1
Frame rate mode                : Constant
Frame rate                     : 23.976 (24000/1001) FPS
Original frame rate            : 23.976 (23976/1000) FPS
Color space                    : YUV
Chroma subsampling             : 4:2:0
Bit depth                      : 8 bits
Bits/(Pixel*Frame)             : 0.218
Stream size                    : 6.53 GiB (88%)
Writing library                : x265 2.2+2-998d4520d1cf:[Windows][GCC 6.2.0][64 bit] 8bit+10bit+12bit
Language                       : Korean
Default                        : Yes
Forced                         : No
yuv  [info]: 1920x804 fps 23976/1000 i420p8 unknown frame count
x265 [info]: HEVC encoder version 2.2+2-998d4520d1cf
x265 [info]: build info [Windows][GCC 6.2.0][64 bit] 8bit+10bit+12bit
x265 [info]: using cpu capabilities: MMX2 SSE2Fast LZCNT
x265 [info]: Main profile, Level-4 (Main tier)
x265 [info]: Thread pool created using 6 threads
x265 [info]: Slices                              : 1
x265 [info]: frame threads / pool features       : 8 / wpp(13 rows)
x265 [info]: Coding QT: max CU size, min CU size : 64 / 16
x265 [info]: Residual QT: max TU size, max depth : 32 / 1 inter / 1 intra
x265 [info]: ME / range / subpel / merge         : star / 57 / 0 / 2
x265 [info]: Keyframe min / max / scenecut / bias: 23 / 250 / 0 / 5.00
x265 [info]: Lookahead / bframes / badapt        : 5 / 3 / 0
x265 [info]: b-pyramid / weightp / weightb       : 1 / 0 / 0
x265 [info]: References / ref-limit  cu / depth  : 1 / off / off
x265 [info]: AQ: mode / str / qg-size / cu-tree  : 1 / 0.0 / 32 / 1
x265 [info]: Rate Control / qCompress            : ABR-8000 kbps / 0.60
x265 [info]: tools: rd=2 psy-rd=2.00 early-skip rskip tmvp fast-intra
x265 [info]: tools: strong-intra-smoothing lslices=5 deblock
x265 [info]: frame I:    668, Avg QP:13.49  kb/s: 32792.61
x265 [info]: frame P:  42215, Avg QP:15.42  kb/s: 15898.10
x265 [info]: frame B: 124086, Avg QP:17.92  kb/s: 5236.86 

Audio
ID                             : 2
Format                         : MLP FBA
Format/Info                    : Meridian Lossless Packing FBA
Commercial name                : Dolby TrueHD
Codec ID                       : A_TRUEHD
Duration                       : 1 h 56 min
Bit rate mode                  : Variable
Bit rate                       : 1 025 kb/s
Maximum bit rate               : 2 562 kb/s
Channel(s)                     : 6 channels
Channel layout                 : L R C LFE Ls Rs
Sampling rate                  : 48.0 kHz
Frame rate                     : 1 200.000 FPS (40 SPF)
Compression mode               : Lossless
Stream size                    : 851 MiB (11%)
Language                       : Korean
Default                        : Yes
Forced                         : No

Text #1
ID                             : 3
Format                         : PGS
Muxing mode                    : zlib
Codec ID                       : S_HDMV/PGS
Codec ID/Info                  : Picture based subtitle format used on BDs/HD-DVDs
Duration                       : 1 h 52 min
Bit rate                       : 21.4 kb/s
Count of elements              : 2922
Stream size                    : 17.3 MiB (0%)
Language                       : Chinese
Default                        : Yes
Forced                         : No

Text #2
ID                             : 4
Format                         : PGS
Muxing mode                    : zlib
Codec ID                       : S_HDMV/PGS
Codec ID/Info                  : Picture based subtitle format used on BDs/HD-DVDs
Duration                       : 1 h 52 min
Bit rate                       : 22.2 kb/s
Count of elements              : 2922
Stream size                    : 17.9 MiB (0%)
Language                       : Chinese
Default                        : No
Forced                         : No

</pre></div>
</td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">IMDb信息</td><td class="rowfollow" valign="top" align="left">IMDb信息未获取，点击<a href="retriver.php?id=71945&amp;type=1&amp;siteid=1"><b>这里</b></a>重新检索IMDb</td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right"><p>豆瓣信息</p></td><td class="rowfollow" valign="top" align="left"><a href="retriver.php?id=71945&amp;type=2&amp;siteid=3">更新</a></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">种子文件</td><td class="rowfollow" valign="top" align="left"><table><tr><td class="no_border_wide"><b>文件数：</b>5个文件<br /><span id="showfl"><a href="javascript: viewfilelist(71945)" >[查看列表]</a></span><span id="hidefl" style="display: none;"><a href="javascript: hidefilelist()">[隐藏列表]</a></span></td></tr></table><span id='filelist'></span></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">热度表</td><td class="rowfollow" valign="top" align="left"><table><tr><td class="no_border_wide"><b>查看: </b>73</td><td class="no_border_wide"><b>点击: </b>7</td><td class="no_border_wide"><b><b>完成:</b> </b><a href="viewsnatches.php?id=71945"><b>3</b>次</a> &lt;--- 点击查看完成详情</td><td class="no_border_wide"><b>最近活动：</b><span title="2020-07-04 05:54:21">6时39分前</span></td></tr></table></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">发布者带宽</td><td class="rowfollow" valign="top" align="left"><img class="speed_down" src="pic/trans.gif" alt="Downstream Rate" /> 100Mbit&nbsp;&nbsp;&nbsp;&nbsp;<img class="speed_up" src="pic/trans.gif" alt="Upstream Rate" /> 100Mbit&nbsp;&nbsp;&nbsp;&nbsp;中国电信</td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right"><span id="seeders"></span><span id="leechers"></span>同伴<br /><span id="showpeer"><a href="javascript: viewpeerlist(71945);" class="sublink">[查看列表]</a></span><span id="hidepeer" style="display: none;"><a href="javascript: hidepeerlist();" class="sublink">[隐藏列表]</a></span></td><td class="rowfollow" valign="top" align="left"><div id="peercount"><b>3个做种者</b> | <b>1个下载者</b></div><div id="peerlist"></div></td></tr>
<tr><td class="rowhead nowrap" valign="top" align="right">感谢者</td><td class="rowfollow" valign="top" align="left"><span id="thanksadded" style="display: none;"><input class="btn" type="button" value="感谢表示成功！" disabled="disabled" /></span><span id="curuser" style="display: none;"><span class="nowrap"><a  href="userdetails.php?id=18394" class='CrazyUser_Name'><b>sungold</b></a></span> </span><span id="thanksbutton"><input class="btn" type="button" id="saythanks" onclick="saythanks(71945);"  value="&nbsp;&nbsp;说谢谢&nbsp;&nbsp;" /><input type="button" class="saythanks" value="+50" onclick="thanksBonus(71945,50);"/><input type="button" class="saythanks" value="+100" onclick="thanksBonus(71945,100);"/><input type="button" class="saythanks" value="+200" onclick="thanksBonus(71945,200);"/><input type="button" class="saythanks" value="+500" onclick="thanksBonus(71945,500);"/><input type="button" class="saythanks" value="+1000" onclick="thanksBonus(71945,1000);"/><input type="button" class="saythanks" value="+2000" onclick="thanksBonus(71945,2000);"/><input type="button" class="saythanks" value="+3000" onclick="thanksBonus(71945,3000);"/><input type="button" class="saythanks" value="+5000" onclick="thanksBonus(71945,5000);"/><input type="button" class="saythanks" value="+10000" onclick="thanksBonus(71945,10000);"/><input id="owner_name" type="hidden" value="parlia"/></span>&nbsp;&nbsp;<span id="nothanks"></span><span id="addcuruser"></span><span class="nowrap"><a  href="userdetails.php?id=11607" class='PowerUser_Name'><b>cccp71</b></a></span> <span class="nowrap"><a  href="userdetails.php?id=9140" class='User_Name'><b>toutiao</b></a></span> <span class="nowrap"><a  href="userdetails.php?id=15787" class='EliteUser_Name'><b>Captiva</b></a></span> </td></tr>
</table>
<br /><br /><table style='border:1px solid #000000;'><tr><td class="text" align="center"><b>快速评论<br /> <br /><font color="#AA0000">严禁纯表情回帖以及“多谢”“good”“求FREE”等无意义回帖 <br /><br />违者将得到一个警告，请和谐讨论</b><br /><br /><form id="compose" name="comment" method="post" action="comment.php?action=add&amp;type=torrent" onsubmit="return postvalid(this);"><input type="hidden" name="pid" value="71945" /><br /><textarea name='body' id="replaytext" cols="100" rows="8" style="width: 450px" onkeydown="ctrlenter(event,'compose','qr')"></textarea><div align="center"><a href="javascript: SmileIT('[em12]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/12.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/12.gif" alt="" /></a><a href="javascript: SmileIT('[em9]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/9.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/9.gif" alt="" /></a><a href="javascript: SmileIT('[em6]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/6.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/6.gif" alt="" /></a><a href="javascript: SmileIT('[em11]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/11.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/11.gif" alt="" /></a><a href="javascript: SmileIT('[em23]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/23.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/23.gif" alt="" /></a><a href="javascript: SmileIT('[em21]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/21.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/21.gif" alt="" /></a><a href="javascript: SmileIT('[em24]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/24.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/24.gif" alt="" /></a><a href="javascript: SmileIT('[em27]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/27.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/27.gif" alt="" /></a><a href="javascript: SmileIT('[em36]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/36.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/36.gif" alt="" /></a><a href="javascript: SmileIT('[em25]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/25.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/25.gif" alt="" /></a><a href="javascript: SmileIT('[em35]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/35.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/35.gif" alt="" /></a><a href="javascript: SmileIT('[em54]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/54.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/54.gif" alt="" /></a><a href="javascript: SmileIT('[em48]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/48.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/48.gif" alt="" /></a><a href="javascript: SmileIT('[em43]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/43.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/43.gif" alt="" /></a><a href="javascript: SmileIT('[em31]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/31.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/31.gif" alt="" /></a><a href="javascript: SmileIT('[em44]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/44.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/44.gif" alt="" /></a><a href="javascript: SmileIT('[em34]','comment','body')"  onmouseover="domTT_activate(this, event, 'content', '&lt;table&gt;&lt;tr&gt;&lt;td&gt;&lt;img src=\'pic/smilies/34.gif\' alt=\'\' /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;', 'trail', false, 'delay', 0,'lifetime',10000,'styleClass','smilies','maxWidth', 400);"><img style="max-width: 25px;" src="pic/smilies/34.gif" alt="" /></a></div><br /><input type="submit" id="qr" class="btn" value="&nbsp;&nbsp;添加&nbsp;&nbsp;" /></form></td></tr></table><p align="center"><a class="index" href="comment.php?action=add&amp;pid=71945&amp;type=torrent">添加评论</a></p>
</td></tr></table><div id="footer"><div style="margin-top: 10px; margin-bottom: 30px;" align="center"> (c)  <a href="https://www.joyhd.net" target="_self">JoyHD</a> 2013-2020 Powered by <a href="aboutnexus.php">NexusPHP</a><br />下载软件：本站不支持迅雷等软件,下载<b><a href=utorrent204_JOYHD.7z>uTorrent</a></b>， 交流群：316052784<br /><a target=_blank href='http://ipv6-test.com/validate.php?url=referer'><img src='pic/button-ipv6-small.png' alt='ipv6 ready' title='ipv6 ready' border='0' /></a></div>
<div style="display: none;" id="lightbox" class="lightbox"></div><div style="display:none;" id="curtain" class="curtain"></div><div id="extraDiv1"></div><div id="extraDiv2"></div></div></body></html>
'''

from pt_site import *
def DebugLog(Str):
    print(Str)

#request_free("unknow",1)
#request_detail('JoyHD','71945')

Nation = Name = Director = Actors = DoubanScore = DoubanID = DoubanLink = IMDBLink = IMDBScore = IMDBID = ""
SummaryStr = re.sub(u'\u3000',u' ',SummaryStr)
SummaryStr = re.sub(u'\xa0', u' ', SummaryStr)
SummaryStr = re.sub('&nbsp;',' ',  SummaryStr)
SummaryStr = SummaryStr.lower()
#DebugLog(SummaryStr)
        
tIndex = SummaryStr.find("豆瓣评分")
if tIndex >= 0 :
    tempstr = SummaryStr[tIndex+5:tIndex+16]
    tSearch = re.search("[0-9]\.[0-9]",tempstr)
    if tSearch : DoubanScore = tSearch.group()
    else:        DoubanScore = ""
    DebugLog("douban score:"+DoubanScore)
else: DebugLog("douban score:not find")

tIndex = SummaryStr.find("豆瓣链接")
if tIndex >= 0 :
    tempstr = SummaryStr[tIndex:]
    tIndex = tempstr.find("href=")
    if tIndex >= 0:
        tempstr = tempstr[tIndex+6:]
        tIndex = tempstr.find('\"')
        if tIndex >= 0 : DoubanLink = tempstr[:tIndex]; DebugLog("douban link:"+DoubanLink)
        else: DebugLog("douban link:error:not find \"")
    else: DebugLog("douban link:error:not find href=")
else: DebugLog("douban link:not find")
DoubanID = get_id_from_link(DoubanLink, DOUBAN)
DebugLog("DoubanLink:"+DoubanLink)

if   SummaryStr.find("imdb评分")    >= 0: tIndex = SummaryStr.find("imdb评分")           
elif SummaryStr.find('imdb.rating') >= 0: tIndex = SummaryStr.find('imdb.rating')
elif SummaryStr.find('imdb rating') >= 0: tIndex = SummaryStr.find('imdb rating')            
else: tIndex = -1               
if tIndex >= 0 :
    tempstr = SummaryStr[tIndex+6:tIndex+36]
    tSearch = re.search("[0-9]\.[0-9]",tempstr)
    if tSearch :  IMDBScore = tSearch.group()
DebugLog("imdb score:"+IMDBScore)

if   SummaryStr.find("imdb链接")    >= 0: tIndex = SummaryStr.find("imdb链接")
elif SummaryStr.find('imdb.link')   >= 0: tIndex = SummaryStr.find("imdb.link")
elif SummaryStr.find('imdb link')   >= 0: tIndex = SummaryStr.find("imdb link")
elif SummaryStr.find('imdb url')    >= 0: tIndex = SummaryStr.find('idmb url')           
else                                    : tIndex = -1            
if tIndex >= 0 :
    tempstr = SummaryStr[tIndex:tIndex+200]
    tIndex = tempstr.find("href=")
    if tIndex >= 0:
        tempstr = tempstr[tIndex+6:]
        tIndex = tempstr.find('\"')
        if tIndex >= 0 : IMDBLink = tempstr[:tIndex]
        else:  DebugLog("imdb link:error:not find \"")
    else:
        tIndex = tempstr.find('http')
        if tIndex >= 0:
            tempstr = tempstr[tIndex:]
            tIndex = tempstr.find('<')
            if tIndex >= 0 : IMDBLink = tempstr[:tIndex] 
IMDBID = get_id_from_link(IMDBLink, IMDB)
DebugLog("imdb link:"+IMDBLink)

if   SummaryStr.find("国  家")    >= 0: tIndex = SummaryStr.find("国  家")
elif SummaryStr.find("产  地")    >= 0: tIndex = SummaryStr.find("产  地")
else                                  : tIndex = -1
if tIndex >= 0 :
    Nation = SummaryStr[tIndex+5:tIndex+20]
    if Nation.find('\n') >= 0: Nation = Nation[:Nation.find('\n')]
    if Nation.find('<')  >= 0: Nation = Nation[ :Nation.find('<') ]
    if Nation.find('/')  >= 0: Nation = Nation[ :Nation.find('/') ]
    Nation = Nation.strip()
    if   Nation[-1:] == '国' : Nation = Nation[:-1]  #去除国家最后的国字
    elif Nation == '香港'    : Nation = '港'
    elif Nation == '中国香港': Nation = '港'
    elif Nation == '中国大陆': Nation = '国'
    elif Nation == '中国台湾': Nation = '台'
    elif Nation == '日本'    : Nation = '日'
    else : pass
    DebugLog("Nation:"+Nation)
else: DebugLog("failed find nation")

tIndex = SummaryStr.find("类  别") 
if tIndex >= 0 and SummaryStr[tIndex:tIndex+100].find("纪录") >= 0 : Type = RECORD
elif SummaryStr.find("集  数") >= 0                                : Type = TV
else                                                               : Type = MOVIE
DebugLog("type:"+str(Type))

if Nation == '港' or Nation == '国' or Nation == '台' : tIndex = SummaryStr.find("片  名")
else                                                  : tIndex = SummaryStr.find("译  名")
if tIndex >= 0 :
    Name = SummaryStr[tIndex+5:tIndex+100]
    if   Name.find("/")  >= 0 : Name = (Name[ :Name.find("/") ]).strip() 
    elif Name.find("<")  >= 0 : Name = (Name[ :Name.find("<") ]).strip() 
    elif Name.find('\n') >= 0 : Name = (Name[ :Name.find('\n') ]).strip()
    else: DebugLog("failed find name"); Name = ""
else: DebugLog("failed find name"); Name = ""
#ExecLog("name:"+Name)
if Name.find('<') >= 0 : Name = Name[:Name.find('<')]
DebugLog("name:"+Name)

tIndex = SummaryStr.find("导  演")
if tIndex >= 0 :
    Director = SummaryStr[tIndex+5:tIndex+100]
    tEndIndex = Director.find('\n')
    if tEndIndex >= 0 : Director = Director[:tEndIndex]
    else : Director = ""
    Director = (Director[ :Director.find('<') ]).strip()
else :Director = ""
DebugLog("director:"+Director)
