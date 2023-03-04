class OpenGraphMixin:
    def get_graph_image(self):
        return None

    def get_graph_description(self):
        return self.search_description if self.search_description else ""
