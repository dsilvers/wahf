from wagtail import hooks


@hooks.register("construct_main_menu")
def reorder_menu_items(request, menu_items):
    for item in menu_items:
        match item.name:
            # members 90
            # explorer 100
            case "images":
                item.order = 110
            case "documents":
                item.order = 120
            # people 130
            case "snippets":
                item.order = 140
            case "_":
                pass
        # print(item.name, item.order)
        # if item.name == 'explorer':  # internal name for the Pages menu item
        #    item.order = 100000
        #    break
