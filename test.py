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
        self.assertTrue(resp.status == 200)

        result = await resp.json()
        self.assertTrue("result" in result)
        self.assertTrue(isinstance(result["result"], dict))
        self.assertTrue("comment_token" in result["result"])
        self.assertTrue(isinstance(result["result"]["comment_token"], str))

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
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], dict))
        self.assertTrue("comment_token" in resp1_result["result"])
        self.assertTrue(isinstance(resp1_result["result"]["comment_token"], str))

        # Add reply for comment
        resp2 = await self.client.post(
            "/api/reply/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_add_reply_replier",
                "text": "Lol, WTF? Not so interesting!"
            }
        )
        self.assertTrue(resp2.status == 200)

        resp2_result = await resp2.json()
        self.assertTrue("result" in resp2_result)
        self.assertTrue(isinstance(resp2_result["result"], dict))
        self.assertTrue("comment_token" in resp2_result["result"])
        self.assertTrue(isinstance(resp2_result["result"]["comment_token"], str))

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
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], dict))
        self.assertTrue("comment_token" in resp1_result["result"])
        self.assertTrue(isinstance(resp1_result["result"]["comment_token"], str))

        # Edit comment
        resp2 = await self.client.post(
            "/api/edit/{comment_token}/test_edit_comment".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "text": "Sorry, I don't think so :("
            }
        )
        self.assertTrue(resp2.status == 200)

        resp2_result = await resp2.json()
        self.assertTrue("result" in resp2_result)
        self.assertTrue(isinstance(resp2_result["result"], bool))
        self.assertTrue("success" in resp2_result["result"])
        self.assertTrue(resp2_result["result"]["success"])

        # Edit message with same text value
        resp3 = await self.client.post(
            "/api/edit/{comment_token}/test_edit_comment".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "text": "Sorry, I don't think so :("
            }
        )
        self.assertTrue(resp3.status == 200)

        resp3_result = await resp3.json()
        self.assertTrue("result" in resp3_result)
        self.assertTrue(isinstance(resp3_result["result"], bool))
        self.assertTrue("success" in resp3_result["result"])
        self.assertTrue(not resp3_result["result"]["success"])

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
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], dict))
        self.assertTrue("comment_token" in resp1_result["result"])
        self.assertTrue(isinstance(resp1_result["result"]["comment_token"], str))

        # Delete comment
        resp2 = await self.client.post(
            "/api/remove/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_remove_comment"
            }
        )
        self.assertTrue(resp2.status == 200)

        resp2_result = await resp2.json()
        self.assertTrue("result" in resp2_result)
        self.assertTrue(isinstance(resp2_result["result"], bool))
        self.assertTrue("success" in resp2_result["result"])
        self.assertTrue(resp2_result["result"]["success"])

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
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], dict))
        self.assertTrue("comment_token" in resp1_result["result"])
        self.assertTrue(isinstance(resp1_result["result"]["comment_token"], str))

        # Add reply for comment
        resp2 = await self.client.post(
            "/api/reply/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_remove_comment2_replier",
                "text": "Lol, WTF? Not so interesting!"
            }
        )
        self.assertTrue(resp2.status == 200)

        resp2_result = await resp2.json()
        self.assertTrue("result" in resp2_result)
        self.assertTrue(isinstance(resp2_result["result"], dict))
        self.assertTrue("comment_token" in resp2_result["result"])
        self.assertTrue(isinstance(resp2_result["result"]["comment_token"], str))

        # Delete comment
        resp3 = await self.client.post(
            "/api/remove/{comment_token}".format(comment_token=resp1_result["result"]["comment_token"]),
            json={
                "user_token": "test_remove_comment2"
            }
        )
        self.assertTrue(resp3.status == 200)

        resp3_result = await resp3.json()
        self.assertTrue("result" in resp3_result)
        self.assertTrue(isinstance(resp3_result["result"], bool))
        self.assertTrue("success" in resp3_result["result"])
        self.assertFalse(resp3_result["result"]["success"])

    @unittest_run_loop
    async def test_get_comments(self):
        async def insert_comment(idx):
            resp = await self.client.post(
                "/api/reply/type2/entity1",
                json={
                    "user_token": "test_get_comments_user_{}".format(idx),
                    "text": "Short message #{} for test_get_comments example".format(idx)
                }
            )
            self.assertTrue(resp.status == 200)

            result = await resp.json()
            self.assertTrue("result" in result)
            self.assertTrue(isinstance(result["result"], dict))
            self.assertTrue("comment_token" in result["result"])
            self.assertTrue(isinstance(result["result"]["comment_token"], str))
            return result["result"]["comment_token"]

        comment_tokens = [await insert_comment(i) for i in range(1000)]

        # Read1
        resp1 = await self.client.get("/api/comments/type2/entity1")
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], list))
        self.assertTrue(len(resp1_result["result"]) == 1000)
        for item in resp1_result["result"]:
            self.assertTrue(isinstance(item, dict))
            self.assertTrue("text" in item)
            self.assertTrue("created" in item)
            self.assertTrue("updated" in item)
            self.assertTrue("user" in item)
            self.assertTrue("key" in item)
            self.assertTrue("parent_key" in item)
            self.assertTrue(item["key"] in comment_tokens)

        # Read2
        resp1 = await self.client.get("/api/comments/type2/entity1/100")
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], list))
        self.assertTrue(len(resp1_result["result"]) == 100)
        for item in resp1_result["result"]:
            self.assertTrue(isinstance(item, dict))
            self.assertTrue("text" in item)
            self.assertTrue("created" in item)
            self.assertTrue("updated" in item)
            self.assertTrue("user" in item)
            self.assertTrue("key" in item)
            self.assertTrue("parent_key" in item)
            self.assertTrue(item["key"] in comment_tokens)

        # Read3
        resp1 = await self.client.get("/api/comments/type2/entity1/100/100")
        self.assertTrue(resp1.status == 200)

        resp1_result = await resp1.json()
        self.assertTrue("result" in resp1_result)
        self.assertTrue(isinstance(resp1_result["result"], list))
        self.assertTrue(len(resp1_result["result"]) == 100)
        for item in resp1_result["result"]:
            self.assertTrue(isinstance(item, dict))
            self.assertTrue("text" in item)
            self.assertTrue("created" in item)
            self.assertTrue("updated" in item)
            self.assertTrue("user" in item)
            self.assertTrue("key" in item)
            self.assertTrue("parent_key" in item)
            self.assertTrue(item["key"] in comment_tokens)


if __name__ == '__main__':
    # os.environ["DATABASE_URL"] = "postgresql://capuchin:passwd@localhost:port/monkey_tester"
    unittest.main()
