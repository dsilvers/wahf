from wagtail import blocks


class BlockQuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(required=True, label="Quote")
    # attribution = blocks.CharBlock(required=False, label="Attribution")

    class Meta:
        icon = "openquote"
        label = "Blockquote"
        template = "blocks/blockquote.html"


class EditorsNoteBlock(blocks.StructBlock):
    note = blocks.TextBlock(required=True, label="Editor's Note")

    class Meta:
        icon = "openquote"
        label = "Editors Note"
        template = "blocks/editors_note.html"
