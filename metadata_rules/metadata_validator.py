import metadata_reader as meta_reader

mr = meta_reader.MetadataReader("personinntekt_eksempel.json")

### List of errors
error_list = []
def add_error(error_text:str):
    error_list.append(error_text)


### Metadata-kontroller (regler) for klargjorte datasett (til arkiv og gjenbruk)
if not mr.get_dataset_name():
    add_error("ERROR: Dataset name missing!")

if not mr.get_dataset_description():
    add_error("ERROR: Dataset description missing!")

# Sjekk at datasettet har en gyldig Unit Type
unit_type_id = mr.get_logical_record_unit_type_id()
if not unit_type_id:
    add_error("ERROR: No Unit Type defined for dataset!")
elif not mr.get_concept_unit_type(unit_type_id):
    add_error("ERROR: Unit Type " + unit_type_id + " does not exist in Concept LDS!")

# Sjekk at det finnes minst 1 identifier-variabel
if len(mr.get_identifier_instance_variable_names()) < 1:
    add_error("ERROR: Missing IDENTIFIER variable in dataset!")

# Sjekk at det finnes minst 1 measure-variable
if len(mr.get_measure_instance_variable_names()) < 1:
    add_error("ERROR: Missing MEASURE variable in dataset!")

# Sjekk at indentifier-variablene peker på en gyldig RepresentedVariable
for var_name in mr.get_measure_instance_variable_names():
    repr_var_id = mr.get_instance_variable_represented_variable_id(var_name)
    if not repr_var_id:
        add_error("ERROR: No Represented Variable ID defined for Identifier variable " + var_name + "!")
    elif not mr.get_concept_represented_variable(repr_var_id):
        add_error("ERROR: Represented Variable with ID " + repr_var_id + " for " + var_name + " does not exist in Concept LDS!")

# Sjekk at measure-variablene peker på en gyldig RepresentedVariable
for var_name in mr.get_measure_instance_variable_names():
    repr_var_id = mr.get_instance_variable_represented_variable_id(var_name)
    if not repr_var_id:
        add_error("ERROR: No Represented Variable ID defined for Measure variable " + var_name + "!")
    elif not mr.get_concept_represented_variable(repr_var_id):
        add_error("ERROR: Represented Variable with ID " + repr_var_id + " for " + var_name + " does not exist in Concept LDS!")

# TODO: Flere metadata-kontroller ...


# Print validation result
if len(error_list) > 0:
    print("")
    print("Metadata validation error(s):")
    for error in error_list:
        print("  " + str(error))
    print("")
else:
    print("")
    print("OK - metadata validation complete :-)")
    print("")
