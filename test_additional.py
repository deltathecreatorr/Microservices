###############################################################
## test_additional.py                                        ##
###############################################################
import requests
import unittest
import database

LLM        = "http://localhost:3000/llm"
GUARDRAILS = "http://localhost:3001/guardrails"
AUBERGE    = "http://localhost:3002/auberge"

class Testing(unittest.TestCase):

  def test_006_guardrails_list_empty(self):
    database.db.clear()

    rsp = requests.get(GUARDRAILS)
    self.assertEqual(rsp.status_code,200)
    self.assertEqual(rsp.json(),[])

  ############################################################
  ## test_007_guardrails_list_multiple                     ##
  ############################################################
  def test_007_guardrails_list_multiple(self):
    database.db.clear()

    data = [
      {"id":"one","regx":"a","sub":"b"},
      {"id":"two","regx":"c","sub":"d"},
      {"id":"three","regx":"e","sub":"f"}
    ]

    for g in data:
      rsp = requests.put(f'{GUARDRAILS}/{g["id"]}',json=g)
      self.assertEqual(rsp.status_code,201)

    rsp = requests.get(GUARDRAILS)
    self.assertEqual(rsp.status_code,200)

    ids = rsp.json()
    self.assertTrue("one" in ids)
    self.assertTrue("two" in ids)
    self.assertTrue("three" in ids)

  ############################################################
  ## test_008_guardrails_delete                            ##
  ############################################################
  def test_008_guardrails_delete(self):
    database.db.clear()

    js = {"id":"delete-me","regx":"x","sub":"y"}
    rsp = requests.put(f'{GUARDRAILS}/delete-me',json=js)
    self.assertEqual(rsp.status_code,201)

    rsp = requests.delete(f'{GUARDRAILS}/delete-me')
    self.assertEqual(rsp.status_code,200)

    rsp = requests.get(f'{GUARDRAILS}/delete-me')
    self.assertEqual(rsp.status_code,404)

  ############################################################
  ## test_009_guardrails_delete_missing                    ##
  ############################################################
  def test_009_guardrails_delete_missing(self):
    database.db.clear()

    rsp = requests.delete(f'{GUARDRAILS}/does-not-exist')
    self.assertEqual(rsp.status_code,404)

  ############################################################
  ## test_010_guardrails_get_missing                       ##
  ############################################################
  def test_010_guardrails_get_missing(self):
    database.db.clear()

    rsp = requests.get(f'{GUARDRAILS}/unknown')
    self.assertEqual(rsp.status_code,404)

  ############################################################
  ## test_011_guardrails_duplicate_id                      ##
  ############################################################
  def test_011_guardrails_duplicate_id(self):
    database.db.clear()

    js = {"id":"dup","regx":"a","sub":"b"}
    rsp = requests.put(f'{GUARDRAILS}/dup',json=js)
    self.assertEqual(rsp.status_code,201)

    rsp = requests.put(f'{GUARDRAILS}/dup',json=js)
    self.assertEqual(rsp.status_code,400)  # duplicate should fail

  ############################################################
  ## test_012_guardrails_missing_field                     ##
  ############################################################
  def test_012_guardrails_missing_field(self):
    database.db.clear()

    js = {"id":"bad","regx":"a"}  # missing sub
    rsp = requests.put(f'{GUARDRAILS}/bad',json=js)
    self.assertEqual(rsp.status_code,400)

  ############################################################
  ## test_013_auberge_input_sanitised                      ##
  ############################################################
  def test_013_auberge_input_sanitised(self):
    database.db.clear()

    js = {"id":"badword","regx":"silver","sub":"metal"}
    requests.put(f'{GUARDRAILS}/badword',json=js)

    js2 = {"prompt":"What is silver?"}
    rsp = requests.post(AUBERGE,json=js2)

    self.assertEqual(rsp.status_code,200)
    self.assertFalse("silver" in rsp.json()["output"])

  ############################################################
  ## test_014_auberge_output_sanitised                     ##
  ############################################################
  def test_014_auberge_output_sanitised(self):
    database.db.clear()

    js = {"id":"censor","regx":"961","sub":"***"}
    requests.put(f'{GUARDRAILS}/censor',json=js)

    js2 = {"prompt":"What is the melting point of silver?"}
    rsp = requests.post(AUBERGE,json=js2)

    self.assertEqual(rsp.status_code,200)
    self.assertFalse("961" in rsp.json()["output"])

  ############################################################
  ## test_015_auberge_multiple_replacements                ##
  ############################################################
  def test_015_auberge_multiple_replacements(self):
    database.db.clear()

    requests.put(f'{GUARDRAILS}/r1',
                 json={"id":"r1","regx":"Rome","sub":"Roma"})

    requests.put(f'{GUARDRAILS}/r2',
                 json={"id":"r2","regx":"Italy","sub":"Italia"})

    js = {"prompt":"What are the major cities of Italy including Rome?"}
    rsp = requests.post(AUBERGE,json=js)

    self.assertEqual(rsp.status_code,200)
    self.assertTrue("Roma" in rsp.json()["output"])
    self.assertTrue("Italia" in rsp.json()["output"])

  ############################################################
  ## test_016_auberge_missing_prompt                       ##
  ############################################################
  def test_016_auberge_missing_prompt(self):
    database.db.clear()

    rsp = requests.post(AUBERGE,json={})
    self.assertEqual(rsp.status_code,400)

  ############################################################
  ## test_017_llm_missing_prompt                           ##
  ############################################################
  def test_017_llm_missing_prompt(self):
    rsp = requests.post(LLM,json={})
    self.assertEqual(rsp.status_code,400)

  ############################################################
  ## test_018_llm_invalid_json                             ##
  ############################################################
  def test_018_llm_invalid_json(self):
    rsp = requests.post(LLM,data="notjson")
    self.assertTrue(rsp.status_code in [400,415])


if __name__ == "__main__":
  unittest.main()
