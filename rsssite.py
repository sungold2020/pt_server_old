#!/usr/bin/python3
# coding=utf-8

from log import *

IGNORE_DOWNLOAD = 0
MANUAL_DOWNLOAD = 1
AUTO_DOWNLOAD = 2


def filter_by_keywords(title, keywords):
    """
    根据includes,excludes关键字过滤来判断是否满足过滤条件
    如果整个keywords为空，则缺省认为不满足过滤条件
    如果includes/excludes单个关键字为空，则认为该单个条件无过滤，例如includes为空，也就是任何title都满足includes条件
    """
    if keywords is None:
        return False

    title = title.lower()
    t_includes = keywords.get('includes') if keywords.get('includes') else []
    for t_include in t_includes:
        t_include = t_include.lower()
        if title.find(t_include) <= 0:
            rss_log('not include {},ignore it:{}'.format(t_include, title))
            return False

    t_excludes = keywords.get('excludes') if keywords.get('excludes') else []
    for t_exclude in t_excludes:
        t_exclude = t_exclude.lower()
        if title.find(t_exclude) >= 0:
            rss_log('endswith {},ignore it:{}'.format(t_exclude, title))
            return False
    return True


def to_be_downloaded(rss_name, title):
    t_site = g_config.rss_site(rss_name)
    if t_site is None:
        error_log("unknown rss name:" + rss_name)
        return IGNORE_DOWNLOAD

    #
    if t_site.get('auto') is None and t_site.get('manual') is None:
        return AUTO_DOWNLOAD

    # AUTO
    if filter_by_keywords(title, t_site.get('auto')):
        return AUTO_DOWNLOAD
    if filter_by_keywords(title, t_site.get('manual')):
        return MANUAL_DOWNLOAD
    return IGNORE_DOWNLOAD


'''
def filter_by_keywords(self):
    """
    根据auto/manual:includes/excludes关键字进行过滤:
    AUTO
    MANUAL
    REMOVE
    """
    tSite = None
    for tRSS in RSS_LIST:
        if tRSS['name'] == self.rss_name:
            tSite = tRSS
            break
    if tSite == None: ErrorLog("unknown rss name:"+self.rss_name); return False
    
    tIncludes = tSite.get('includes')   if tSite.get('includes') else []
    for tInclude in tIncludes:
        if self.title.find(tInclude) <= 0: 
            rss_log('not include {},ignore it:{}'.format(tInclude,self.title))
            return False

    tExcludes = tSite.get('excludes')   if tSite.get('excludes') else []
    for tExclude in tExcludes:
        if self.title.find(tExclude) >= 0: 
            rss_log('include {},ignore it:{}'.format(tExclude,self.title))
            return False
    return True
'''
