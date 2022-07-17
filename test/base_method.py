class BaseMethod:
    def get_available_link(self, site, app_config):
        links = site.links
        re_links = {}
        for linkname, link in links.items():
            if link.latency <= app_config.latency and \
                    link.jitter <= app_config.jitter and \
                    link.lost <= app_config.lost:
                re_links[link.link_name] = link
        return re_links
