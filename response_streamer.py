import json


class BasicStreamer(object):
    def __init__(self, stream_response):
        self.stream_response = stream_response
        self.got_head = False

    async def write_head(self, data):
        if not self.got_head:
            await self.stream_response.write(data)
            self.got_head = True

    async def write_body(self, data):
        await self.stream_response.write(data)

    async def write_tail(self, data):
        await self.stream_response.write_eof(data)


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
            return "".join(
                "<item key=\"{key}\">{value}</item>".format(
                    key=html_escape(str(key)),
                    value=self.encode_recursive(value))
                for key, value in obj.items()
            )
        elif isinstance(obj, list):
            return "".join(
                "<item_{index}>{value}</item_{index}>".format(
                    index=index,
                    value=self.encode_recursive(value))
                for index, value in enumerate(obj)
            )
        else:
            return html_escape(str(obj))

    async def write_head(self, data=None):
        return await super(XMLStreamer, self).write_head(XMLStreamer.HEADER)

    async def write_tail(self, data=None):
        return await super(XMLStreamer, self).write_tail(XMLStreamer.TAIL)

    async def write_body(self, data):
        return await super(XMLStreamer, self).write_body(self.encode_recursive(data).encode("utf-8"))


class JSONStreamer(BasicStreamer):
    HEADER = b"["
    TAIL = b"]"

    def __init__(self, stream_response):
        super(JSONStreamer, self).__init__(stream_response)
        self.got_first_item = False

    async def write_head(self, data=None):
        return await super(JSONStreamer, self).write_head(JSONStreamer.HEADER)

    async def write_tail(self, data=None):
        return await super(JSONStreamer, self).write_tail(JSONStreamer.TAIL)

    async def write_body(self, data):
        result = await super(JSONStreamer, self).write_body(
            "{}{}".format(
                "," if self.got_first_item else "",
                json.dumps(data)).encode("utf-8")
        )

        self.got_first_item = True

        return result
