import metadata_reader as meta_reader

mr = meta_reader.MetadataReader("personinntekt_eksempel.json")


# Eksempler på regler:
if mr.count_identifier_instance_variables() < 1:
    print("ERROR: Missing IDENTIFIER variable in dataset!")

if mr.count_measure_instance_variables() < 1:
    print("ERROR: Missing MEASURE variable in dataset!")

for var_name in mr.get_instance_variable_names():
    if mr.get_instance_variable_component_type(var_name) == "IDENTIFIER" and mr.get_instance_variable_represented_variable_id(var_name) == None:
        print("ERROR: No Represented Variable for identifier!")


# TODO: Masse jobb gjenstår her!!!