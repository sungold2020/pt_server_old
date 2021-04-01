from ptsite import *


class Sites:
    site_list = []

    @staticmethod
    def get_site_list() -> list:
        return Sites.site_list

    @staticmethod
    def load(site_list: list) -> bool:
        """

        :param site_list:
        :return:
        """
        if site_list is None or len(site_list) == 0:
            Log.error_log("error:init site_list ")
            return False

        for site in site_list:
            pt_site = PTSite(site)
            Sites.site_list.append(pt_site)
        return True

    @staticmethod
    def reload(site_list: list) -> bool:
        """

        :param site_list:
        :return:
        """
        # keep these param's value
        # self.error_count = 0
        # self.last_time = time.time()
        # self.error_string = ""

        for new_site in site_list:
            if not Sites.update_site_config(new_site):
                Log.error_log(f"error:failed to load config for{new_site.get('site_name', '')}")
        return True

    @staticmethod
    def update_site_config(new_site: dict) -> bool:
        """

        :param new_site:
        :return:
        """
        new_pt_site = PTSite(new_site)
        for i in range(len(Sites.site_list)):
            site = Sites.site_list[i]
            if site.site_name == new_pt_site.site_name:
                new_pt_site.error_count = site.error_count
                new_pt_site.error_string = site.error_string
                new_pt_site.last_time = site.last_time
                Sites.site_list[i] = new_pt_site
                return True

        return False

    @staticmethod
    def get_site(site_name: str) -> [None, PTSite]:
        """

        :param site_name:
        :return:
        """
        for site in Sites.site_list:
            if site.site_name.lower() == site_name.lower():
                return site
        return None

    @staticmethod
    def read_tracker_data_backup(tracker_data_file: str = SysConfig.TRACKER_LIST_BACKUP) -> bool:
        """

        :param tracker_data_file:
        :return:
        """
        if not os.path.isfile(tracker_data_file):
            Log.exec_log(f"tracker_list_backup:{tracker_data_file} does not exist")
            return False

        for line in open(tracker_data_file, encoding='UTF-8'):
            site_name, date_data_str = line.split('|', 1)
            if date_data_str[-1:] == '\n':
                date_data_str = date_data_str[:-1]  # remove '\n'
            date_data_list = date_data_str.split(',')
            date_data = []
            for i in range(len(date_data_list)):
                if date_data_list[i] == "":
                    break  # 最后一个可能为空就退出循环
                t_date = (date_data_list[i])[:10]
                t_data = int((date_data_list[i])[11:])
                date_data.append({'date': t_date, 'data': t_data})

            is_find = False
            for site in Sites.site_list:
                if site_name == site.site_name:
                    site.upload_traffic_list = date_data
                    is_find = True
            if not is_find:
                Log.error_log("unknown site in TrackerBackup:" + site_name)
        return True

    @staticmethod
    def write_tracker_data_backup(tracker_data_file: str = SysConfig.TRACKER_LIST_BACKUP) -> bool:
        """

        :param tracker_data_file:
        :return:
        """
        t_today = datetime.datetime.now().strftime('%Y-%m-%d')

        #
        t_this_month = t_today[0:7]
        t_this_year = t_today[0:4]
        if t_this_month[5:7] == "01":
            t_last_month = str(int(t_this_year) - 1) + "-" + "12"
        else:
            t_last_month = t_this_year + "-" + str(int(t_this_month[5:7]) - 1).zfill(2)
        t_file_name = os.path.basename(tracker_data_file)
        t_length = len(t_file_name)
        t_dir_name = os.path.dirname(tracker_data_file)
        for file in os.listdir(t_dir_name):
            if file[:t_length] == t_file_name and len(file) == t_length + 11:  # 说明是TorrentListBackup的每天备份文件
                if file[t_length + 1:t_length + 8] != t_last_month \
                        and file[t_length + 1:t_length + 8] != t_this_month:  # 仅保留这个月和上月的备份文件
                    try:
                        os.remove(os.path.join(t_dir_name, file))
                    except Exception as err:
                        print(err)
                        Log.error_log("failed to delete file:" + os.path.join(t_dir_name, file))

        # 把旧文件备份成today的文件,后缀+"."+today
        t_last_day_file_name = tracker_data_file + "." + t_today
        if os.path.isfile(tracker_data_file):
            if os.path.isfile(t_last_day_file_name):
                os.remove(t_last_day_file_name)
            os.rename(tracker_data_file, t_last_day_file_name)

        try:
            fo = open(tracker_data_file, "w", encoding='UTF-8')
        except Exception as err:
            print(err)
            Log.error_log("Error:open ptbackup file to write：" + SysConfig.TRACKER_LIST_BACKUP)
            return False

        for site in Sites.site_list:
            t_str = site.site_name + '|' + site.get_upload_traffic_list_string() + '\n'
            fo.write(t_str)

        fo.close()
        Log.exec_log("success write tracklist")
        return True

    @staticmethod
    def count_last_day_upload_traffic():
        """
        统计各站点的上传量、总上传量和速率
        统计各站点连续N天无上传
        :return:
        """
        # 统计各站点的上传量和总上传量
        total_upload = 0
        for site in Sites.site_list:
            upload = site.get_last_day_upload_traffic()
            total_upload += upload
            Log.exec_log(f"{site.site_name.ljust(10)} upload(G):{round(upload / (1024 * 1024 * 1024), 3)}")
        Log.exec_log(f"total       upload(G):{round(total_upload / (1024 * 1024 * 1024), 3)}")
        Log.exec_log(f"average upload radio :{round(total_upload / (1024 * 1024 * 24 * 3600), 2)}M/s")

        # 统计各站点连续N天无上传
        for site in Sites.site_list:
            days = site.get_days_of_no_upload()
            Log.exec_log(f"{site.site_name.ljust(10)} {str(days).zfill(2)} days no upload")
