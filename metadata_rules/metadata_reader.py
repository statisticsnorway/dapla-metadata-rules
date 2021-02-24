import json
import pathlib
import requests

class MetadataReader:

    def __init__(self, dapla_json_doc_file):
        self.jupyter_meta = None
        # TODO: Bytte til riktig sti i Jupyter notebook miljøet!!!
        self.__dapla_json_doc_file = dapla_json_doc_file
        self.__project_root_path = pathlib.Path(__file__).parent.parent
        self.__lds_cookie = None
        self.set_cookie()  # TODO: Fjernes hvis Concept LDS API åpnes for les!
        self.__read_dapla_jupyter_metadata()


    # TODO: Forhåpenligvis kan vi fjerne set_cookie() hvis de får åpnet Concept LDS API for les uten pålogging!
    def set_cookie(self):
        self.__lds_cookie = input("Cookie:")


    # Leser metadata fra en Jupyter %document-json-fil 
    def __read_dapla_jupyter_metadata(self):
        # TODO: Lese metadata fra riktig path/filnavn i Jupyter i Dapla notebook miljø.
        path_jupyter_doc_json = self.__project_root_path.joinpath("tests").joinpath("resources").joinpath("example_metadata")
        with open(path_jupyter_doc_json.joinpath(self.__dapla_json_doc_file)) as json_file: 
            self.jupyter_meta = json.load(json_file)

    ##########
    # TODO: DataSet.temporalityType mangler i JSON-filen fra Jupiter %document.
    # TODO: DataSet.dataSetState mangler også. Kanskje vi trenger denne?
    # TODO: Kanskje vi også trenger DataSet.valuation ???
    # TODO: DataSet.shortName???
    # TODO: InstanceVariable.shortName???
    ##########

    # Metodene nedenfor henter ut elementer (objekt og attributter) fra Jupyter %document-json-filen
    def get_dataset_name(self):
        return self.jupyter_meta["name"]

    def get_dataset_description(self):
        return self.jupyter_meta["description"]

    def get_logical_record_unit_type_id(self):
        return self.jupyter_meta["unitType"]["selected-id"]

    def get_instance_variable_list(self):
        return self.jupyter_meta["instanceVariables"]

    def get_instance_variable_names(self):
        names = []
        for inst_var in self.get_instance_variable_list():
            names.append(str(inst_var["name"]))
        return names

    def get_instance_variable(self, name):
        for inst_var in self.get_instance_variable_list():
            if inst_var["name"] == name:
                return inst_var
        return None  # variable not found

    def get_instance_variable_description(self, name):
        return self.get_instance_variable(name)["description"]

    def get_instance_variable_component_type(self, name):
        return self.get_instance_variable(name)["dataStructureComponentType"]["selected-enum"]

    def count_identifier_instance_variables(self):
        cnt = 0
        for inst_var in self.get_instance_variable_list():
            if inst_var["dataStructureComponentType"]["selected-enum"] == "IDENTIFIER":
                cnt+=1
        return cnt

    def count_measure_instance_variables(self):
        cnt = 0
        for inst_var in self.get_instance_variable_list():
            if inst_var["dataStructureComponentType"]["selected-enum"] == "MEASURE":
                cnt+=1
        return cnt

    def get_instance_variable_represented_variable_id(self, name):
        return self.get_instance_variable(name)["representedVariable"]["selected-id"]

    def get_instance_variable_population_id(self, name):
        return self.get_instance_variable(name)["population"]["selected-id"]

    def get_instance_variable_sentinel_value_domain_id(self, name):
        return self.get_instance_variable(name)["sentinelValueDomain"]["selected-id"]


    # Generell funksjon for å hente Concept metadata fra LDS Rest API
    def get_concept_metadata(self, object_type:str, object_id:str=None):
        # Eksempel Stage LDS: https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/RepresentedVariable
        concept_lds_url = "https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/"  # Stage LDS API
        concept_object_url = concept_lds_url + object_type
        if object_id:
            # Eksempel Stage LDS: https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/RepresentedVariable/RepresentedVariable_DUMMY
            concept_object_url = concept_object_url + "/" + object_id
        response = requests.get(concept_object_url, headers={"Cookie": self.__lds_cookie})
        if response.text:
            return requests.get(concept_object_url, headers={"Cookie": self.__lds_cookie}).json()
        else:
            print("ERROR: Not valid request for Concept LDS API or other problems?")
            print("  " + concept_object_url)
            print("  " + str(response))
            return None

    # Metodene nedenfor henter ut elementer (objeker og attributter) fra Concpet LDS
    def get_concept_unit_type(self, id):
        return self.get_concept_metadata("UnitType", id)

    def get_concept_population(self, id):
        return self.get_concept_metadata("Population", id)

    def get_concept_subject_field(self, id):
        return self.get_concept_metadata("SubjectField", id)

    def get_concept_described_value_domain(self, id):
        return self.get_concept_metadata("DescribedValueDomain", id)

    def get_concept_enumerated_value_domain(self, id):
        return self.get_concept_metadata("EnumeratedValueDomain", id)

    def get_concept_represented_variable(self, id):
        return self.get_concept_metadata("RepresentedVariable", id)

    def get_concept_represented_variable_substantive_value_domain(self, id):
        if "DescribedValueDomain/" in id:
            self.get_concept_described_value_domain(id)
        elif "EnumeratedValueDomain/" in id:
            self.get_concept_enumerated_value_domain(id)
        else:
            return None


    # def read_data_concept_metadata(self):
    #     ## Eksempel på hvordan funksjonen kan brukes til å hente ut domene-objekter med ID i LDS.
    #     #print(get_lds_metadata('/RepresentedVariable/f2bdc3f3-5275-40a6-897d-c00a494532fc'))
    #     #print(get_lds_metadata('/Variable/3335298a-779d-4bd4-84a1-3262b8afbbeb'))
    #     #print(get_lds_metadata('/EnumeratedValueDomain/5b30542b-3ed0-4136-8d1e-ebb5097d35af'))
    #     #print(get_lds_metadata('/Population/96869bb9-ebcd-4630-ab73-005a4c4b4674'))
    #     #print(get_lds_metadata('/Universe/6ab622e1-adf1-4739-b549-c482bd901c4d'))
    #     # https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/Population
    #     # https://concept-lds.staging-bip-app.ssb.no/ns/Population/2aa9ab12-63ca-4458-aa00-95ea287bf2a5 
    #     # curl --location --request GET 'https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/Population' --header 'Cookie: _ga=GA1.2.420304463.1559052959; oauth2_proxy=yAo3PcQG2PL....'
    #     #Som du ser så får du også ut LDS-lenker videre til andre objekter (relasjonene), f.eks. EnumeratedValueDomain for skattekommune "/EnumeratedValueDomain/5b30542b-3ed0-4136-8d1e-ebb5097d35af".
    #     #Denne kan du igjen bruke til å kalle
    #     #lds_enumerated_value_domain = get_lds_metadata('/EnumeratedValueDomain/29e2238b-1e5d-46cc-b9dc-1a0f5ec5060d
    #     #/Universe/8fcf88a7-2113-47ad-9226-ea914b4284bd')
    #     #lds_result = requests.get('https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/RepresentedVariable', headers={"Cookie":"_ga=GA1.2.422139094.1583486083; oauth2_proxy=YDvyzBlV2YhOuRhpHhO_EMPKrOwx1CTTJL5nocVmh8AXKlZHxTUPl4uBtlg5BcO4oyROP9iFoY7qMxlaH7kp84X1B8M6ppn15I5uPmh-S3zaDxQn7U55nKL4xeWNGdobvba8HK3i2S3wQY1qe3Ttkr5qpcreQAz3ECmRlVEubv_Rx3Re9zZE1SbhJY3LlCOf_7HMNp3qzrpmg6wKgoa1op5EKU8ZybbRtQFtt68L2CHG4qm2yAUmNCokeB30flsIwvisTTbEBW_xSGmHtJK7d_e6NPcOllrQ-YB4MYpS1fcNSrVBlpZz5j8ez8ug-v0cVd5LwTeIkY1hiEdgEdjVm4V7YP4mkVbeaw4vJTHGxB1MZPEjETkRsmUjlZuYg_naecP6QtoP-77kTzf8obf6grYwwZpZH6PyUDoQcJUVqrmFF91P7OsVAyd8c8GuYz4aZfkYcqsphCDquGPyJKwmlSBzDduYli2Fbu5ysBGm3X6l0HnT5jjCnbDIiqNOby0Y8k2dXjTi8Gmin81fgvnCUa-zRfa8EWO27aXQPXi8OEFs9WDhAbcqdIoQPGPH28yj0ZHa_Df0vBoGCe19OXUGW8ohq_vfrP5XDfqYfhNGs-XK3iG-yQKwQEdH3oZlF3LMXBnDAxilp1CpM8FqV0FT_0H1ZzAelDMryNSXSjCKnWO9TzirOxNZECmjE0zRSKwL0dBD3zDFh8ZZH8WqZ_6jZW7WX2fYdFrlmfCdaCCW_a3pBmavbSBv45vqNJkql3IteJUUrm7b2piy9o350-nOiCH4mGg1oKlxpRLs2GQmK9gw1NPSB4eWXwi3J0R250E9ErU02A0Z-jLlpzE1VW0Dhw3ZsqAUgiMGkG8h_Z4F-EffwHmjV-zcstxbdv_nhGIYrfgxEiAA3YwzjKnduaTeOrlRwbJlDM_Up4xL2sG4jkq9w-rlgsqoKcaQUF0SdyU4hHZXe9Ghqnrv0GtMssdgDTvaJfU435Mnj6WrPNtshG1PS0_44MN8NYvZ3N7yBeY-j0_P4BLdZYDlODgEWd3kPSqIUov3TACr0l2rDQvHiXwzJT4VAw5Wt2d9eyfjMbqGnHEuCnkYqm70pO-5CoRlpcz5K-6kl8U9CVD3RVEEg_5LRonTJfdqV1VbPgBfZQYz3B8zeGIequrewcKiCcf44VqzW7he-jdAUTG71m8DlAlCoAlQcpu256GZ4Gjmd7lVfdsFYZbifYDYAGDBqMVMshrBRuwWFJ6QnAN5Ze4OTWka7k5opIgbTMen3HwLPMutFu7L_SO78NwZJgf96fDAU2a9GRzS4d5Wm8QMa2hjbDKyhtgQZwA_ZquEN_bUn9fBmMaTSUXQ8be1bU8njrczXQKsHnP2HAiCMHS1xIbJB7WnfMQB0dF3Nd6WnTdo0LbBYuunszwwUsdFswPCULRvclDUCFbLmxEzcJY8RiTxSPgUtO2Q8_bNippXHGHh6RfK9zqKZIS5PBclWkIcN2IGImhp4sbMuUh2IPhBm5e1pHeXE7FqP0IcKeCA_PWSl5-xqyX4iUZll-ZYCXbYnNaRRlh502ZUJ0yXaOhYxOEMdzRHmH1x_iZ5Ppp_kWyLR4J4l65e1Az9zdM6rZnyDU9tRdoqg0B4v1Kz5u6xdyI-HUGjNM16ipPaa-7QuUNBJwGudW2GZoYOYciOUBT1HIdqdnYov_nt-KFsWEPdmXGL417SoyKLowlSVQa4vjn2ec79bZI4ZxxVxQWg5NjQS6CcKJ1s62K8m4dpZqyJxv6cH-TIWpWS2rICnoC821JckDAHkHj_ghmpyZBKEK1A7GdRAmhugwCE2DzfNtGVLlPw1amJTRo9xTJW3wjELFuIgDL-PWLciZakKxKvLcWNWu8FZXf6alwjhQj5LpW4Ex6C55m0w7LEmFoRCX8c65xiM-_XX3hYX2UC48CejExM6n-tKfBYzIcYOYi4F8k4bR76XDJOkG-rPhubjyzvQgRphKq_NTrbXAUk-45QikGFpwH43tvG8CGBa4ebvApZkkPXrM5e-Gc76PCuPF86jwuc5_PBdc-61_nl7whCJFera7f72L-HP5lIwAUpe_azgLlY19Jrlvc2OpfsSEOFOc-zZV6UMhC_WatEDyG2aSbmkS7VWbUODrvdo-h4nXt4AtOEGcRgpHwPs0fUO47Q8OUWWOP9kKAXsLYLhS4PfvJLLMgH-MDcMi9v_pSsUzLIOsmf58o8GDbcNXGFLEJJgx1p1fTKg5w3qlDYu6cP-flYueUWVHilRSHIpEfuuSp8HkPqlsBjuteSiO2Abli6ShhQo6ie3XHBRgJxkqsKBL0z395KaabDQk2akBjKBSRrBBMo9G7d3R_q9ovUGzkPS_tf3Zkp7SQmmQcA7hTDKeSJeZsG5G_b5xQuuTTHOsT2dCu1TIzZPpkKElqPaGxcRL_TOY8Ld0T3YVQ1mCD94YVcgXa06AtAnKxJSKKsZbolyP_BUj_BqlY3EOFQSwqNB65CQrQnwKnIIlKHUo3MtHouiWzrc2gSKkOyGIkYTAW5CDOBWWdErgkv55kfIP8061u86bxEWiFQNf8DelWV1jWl7MZDSRGX6X3EeVAjBt90zETGDNGy_XTZHz3_o9zHx7ArC-VbaijKcKEUJcrJktjRNWREeLi128_zzCPluSKd3ZsA5DvxIV1mIOpCt2guvxh7v3G0a9ya9B95EgPFpMH2baJ1nR9l4JGW23ZoIBlnwJMukMkjeCI3vid0NTZdDODW2jy8ZD2hxeISDo4kAiX3dC8li1yMaBGmPaX-ifKGDfu8m-JmR-z4pPFiGV3EScOdXo1pzSKvTq6WHtQ6QhNON1GzMPxhmhFr07g_-Pq9qsljSWDpZneQEp4jAvOSdSUPhldRj_KRqaACadQSSzR6dqszOYy5F8qENDqgxBkvmbTLjg_1xlFlu1KWdyz3ASSPklwTlxIopjAMud-fZT-D502vnUJncGH6SSXMyvPOfUUT356e0PM8Ea-bd6XA4gcLtur7J93-ZbEcFnGIJg7MArMtB_clhoux_oXMq6OAbUYAwRazmL1lM7iEqhTwpI4TaPlJy_XjqQz7eAbgnFoX9Y-h0EVHx5U4mFwwqc7n_GYlnA-fVAhM5LPPJRZ73uCsQbBAAEjywOPjYevSfPRSz0xmCnzEJXZgZwPDB9o9ilaGaj3cn8gq8QFaJVoTEAJaZSKOzuR3TCpg7JLiKVAx09CS4mXpR17FS1C_hjiZjFPs5TPqhfgGSxL7t-1HB-yUPYBDAyx5jmDbXshNty1swrCXrnkzpIdUU6vP38HGHehoXT21BUoSYAWY1HFPIuNCGuWVKYgffOva2c4gXqOi_ZoK4Y1Qmj8eqEktAlNnd9vXdVCbj0DBAaJ9ofNeSmdacAoCzC4AzQUxSxFxaK984RJpwhg79EKo6nCjsRgQzm5_HDKinJP1uMyngJcw5HTpHsnmX-LIRqkXn_iFouDiIW2INhd42s3ccpR_F8AW4dRodVvGniR-3i0rooMX0p0oYp85i4pwQi2GksutQrAs6E5u6uClKF11oKiXY6l9yq55nHWKXdSbWdroq6eFPw2ML2vthb5qHi_LZNA53AlKaOhw-QpqFc3cFyvxouExYKAS4LrSRw0=|1613723881|jev5g3wNmWeQa7HDjfE4SEDaFh6D4pRj_N_mAvUnNu8="} )
    #     key = input("Cookie:")
    #     lds_result = requests.get('https://dapla-workbench.staging-bip-app.ssb.no/be/concept-lds/ns/RepresentedVariable', headers={"Cookie": key} )
    #     #print(lds_result.text)
    #     #print(lds_result.json())
    #     print(json.dumps(lds_result.json(), sort_keys=False, indent=4, ensure_ascii=False))
    #     #return lds_result.json()


# ### Eksempel på bruk:
# mr = MetadataReader("personinntekt_eksempel.json")
# #print(json.dumps(mr.jupyter_meta, sort_keys=False, indent=4))
# print(mr.get_dataset_name())
# print(mr.get_dataset_description())
# print(mr.get_logical_record_unit_type_id())
# #print(mr.get_instance_variables_list())
# print(mr.get_instance_variable_component_type("fnr"))

# print(mr.get_concept_represented_variable("RepresentedVariable_DUMMY"))


