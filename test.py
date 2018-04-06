import unittest

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from app import get_app


class ApplicationTestCase(AioHTTPTestCase):

    async def get_application(self):
        return await get_app()

    @unittest_run_loop
    async def test_add_comment(self):
        resp = await self.client.post(
            "/api/reply/type1/entity1",
            json={
                "user_token": "test_add_comment",
                "text": "Test message"
            }
        )
        assert resp.status == 200

        result = await resp.json()
        assert "result" in result
        assert isinstance(result["result"], dict)
        assert "comment_token" in result["result"]
        assert isinstance(result["result"]["comment_token"], str)

    @unittest_run_loop
    async def test_add_reply(self):
        # Add new comment
        resp1 = await self.client.post(
            "/api/reply/type1/entity1",
            json={
                "user_token": "test_add_reply",
                "text": "Hi, nice video!"
            }
        )
        assert resp1.status == 200

        resp1_result = await resp1.json()
        assert "result" in resp1_result
        assert isinstance(resp1_result["result"], dict)
        assert "comment_token" in resp1_result["result"]
        assert isinstance(resp1_result["result"]["comment_token"], str)

        # Add reply for comment
        resp2 = await self.client.post(
            "/api/reply/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_add_reply_replier",
                "text": "Lol, WTF? Not so interesting!"
            }
        )
        assert resp2.status == 200

        resp2_result = await resp2.json()
        assert "result" in resp2_result
        assert isinstance(resp2_result["result"], dict)
        assert "comment_token" in resp2_result["result"]
        assert isinstance(resp2_result["result"]["comment_token"], str)

    @unittest_run_loop
    async def test_edit_comment(self):
        # Add new comment
        resp1 = await self.client.post(
            "/api/reply/type1/entity1",
            json={
                "user_token": "test_edit_comment",
                "text": "Cooooooooool video!"
            }
        )
        assert resp1.status == 200

        resp1_result = await resp1.json()
        assert "result" in resp1_result
        assert isinstance(resp1_result["result"], dict)
        assert "comment_token" in resp1_result["result"]
        assert isinstance(resp1_result["result"]["comment_token"], str)

        # Edit comment
        resp2 = await self.client.post(
            "/api/edit/{comment_token}/test_edit_comment".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "text": "Sorry, I don't think so :("
            }
        )
        assert resp2.status == 200

        resp2_result = await resp2.json()
        assert "result" in resp2_result
        assert isinstance(resp2_result["result"], bool)
        assert "success" in resp2_result["result"]
        assert resp2_result["result"]["success"]

        # Edit message with same text value
        resp3 = await self.client.post(
            "/api/edit/{comment_token}/test_edit_comment".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "text": "Sorry, I don't think so :("
            }
        )
        assert resp3.status == 200

        resp3_result = await resp3.json()
        assert "result" in resp3_result
        assert isinstance(resp3_result["result"], bool)
        assert "success" in resp3_result["result"]
        assert not resp3_result["result"]["success"]

    @unittest_run_loop
    async def test_remove_comment(self):
        # Add new comment
        resp1 = await self.client.post(
            "/api/reply/type1/entity1",
            json={
                "user_token": "test_remove_comment",
                "text": "I must delete this message..."
            }
        )
        assert resp1.status == 200

        resp1_result = await resp1.json()
        assert "result" in resp1_result
        assert isinstance(resp1_result["result"], dict)
        assert "comment_token" in resp1_result["result"]
        assert isinstance(resp1_result["result"]["comment_token"], str)

        # Delete comment
        resp2 = await self.client.post(
            "/api/remove/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_remove_comment"
            }
        )
        assert resp2.status == 200

        resp2_result = await resp2.json()
        assert "result" in resp2_result
        assert isinstance(resp2_result["result"], bool)
        assert "success" in resp2_result["result"]
        assert resp2_result["result"]["success"]

    @unittest_run_loop
    async def test_remove_comment2(self):
        # Add new comment
        resp1 = await self.client.post(
            "/api/reply/type1/test_remove_comment2",
            json={
                "user_token": "test_user",
                "text": "I must delete this message..."
            }
        )
        assert resp1.status == 200

        resp1_result = await resp1.json()
        assert "result" in resp1_result
        assert isinstance(resp1_result["result"], dict)
        assert "comment_token" in resp1_result["result"]
        assert isinstance(resp1_result["result"]["comment_token"], str)

        # Add reply for comment
        resp2 = await self.client.post(
            "/api/reply/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_remove_comment2_replier",
                "text": "Lol, WTF? Not so interesting!"
            }
        )
        assert resp2.status == 200

        resp2_result = await resp2.json()
        assert "result" in resp2_result
        assert isinstance(resp2_result["result"], dict)
        assert "comment_token" in resp2_result["result"]
        assert isinstance(resp2_result["result"]["comment_token"], str)

        # Delete comment
        resp3 = await self.client.post(
            "/api/remove/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_remove_comment2"
            }
        )
        assert resp3.status == 200

        resp3_result = await resp3.json()
        assert "result" in resp3_result
        assert isinstance(resp3_result["result"], bool)
        assert "success" in resp3_result["result"]
        assert not resp3_result["result"]["success"]


if __name__ == '__main__':
    # os.environ["DATABASE_URL"] = "postgresql://capuchin:passwd@localhost:port/monkey_tester"
    unittest.main()
