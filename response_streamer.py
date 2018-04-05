import json


class BasicStreamer(object):
    def __init__(self, stream_response):
        self.stream_response = stream_response
        self.got_head = False

    def write_head(self, data):
        if not self.got_head:
            self.stream_response.write(data)
            self.got_head = True

    def write_body(self, data):
        self.stream_response.write(data)

    def write_tail(self, data):
        self.stream_response.write_tail(data)


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)


class XMLStreamer(BasicStreamer):
    HEADER = b"<?xml version=\"1.0\" encoding=\"UTF-8\"?><data>"
    TAIL = b"</data>"

    def encode_recursive(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                return "<item key=\"{key}\">{value}</item>".format(key=html_escape(str(key)),
                                                                   value=self.encode_recursive(value))
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                return "<item_{index}>{value}</item_{index}>".format(index=index, value=self.encode_recursive(value))
        else:
            return html_escape(str(obj))

    def write_head(self, data=None):
        super(XMLStreamer, self).write_head(XMLStreamer.HEADER)

    def write_tail(self, data=None):
        super(XMLStreamer, self).write_tail(XMLStreamer.TAIL)

    def write_body(self, data):
        super(XMLStreamer, self).write_body(self.encode_recursive(data).encode("utf-8"))


class JSONStreamer(BasicStreamer):
    HEADER = b"["
    TAIL = b"]"

    def __init__(self, stream_response):
        super(JSONStreamer, self).__init__(stream_response)
        self.got_first_item = False

    def write_head(self, data=None):
        super(JSONStreamer, self).write_head(JSONStreamer.HEADER)

    def write_tail(self, data=None):
        super(JSONStreamer, self).write_tail(JSONStreamer.TAIL)

    def write_body(self, data):
        super(JSONStreamer, self).write_body(
            "{}{}".format(
                "," if self.got_first_item else "",
                json.dumps(data)).encode("utf-8")
        )

        self.got_first_item = True
