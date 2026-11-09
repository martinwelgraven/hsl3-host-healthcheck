""" def parse_xml(file_content):
    root = ET.fromstring(file_content)
    
    assert root.tag == 'module'
    inputs = []
    outputs = []
    stores = []
    timers = []
    scripts = []
    translations = []
    inputs_element = root.find('inputs')
    
    if inputs_element is None:
        raise ValueError("XML is missing required 'inputs' element.")
    for elem in inputs_element:
        list_item = ConfigInput(**elem.attrib)
        inputs.append(list_item)
    
    outputs_element = root.find('outputs')
    if outputs_element is None:
        raise ValueError("XML is missing required 'outputs' element.")
    for elem in outputs_element:
        list_item = ConfigOutput(**elem.attrib)
        outputs.append(list_item)
    
    stores_element = root.find('stores')
    if stores_element is None:
        raise ValueError("XML is missing required 'stores' element.")
    for elem in stores_element:
        list_item = ConfigStore(**elem.attrib)
        stores.append(list_item)
    
    timers_element = root.find('timers')
    if timers_element is None:
        raise ValueError("XML is missing required 'timers' element.")
    for elem in timers_element:
        list_item = ConfigTimer(**elem.attrib)
        timers.append(list_item)
    
    scripts_element = root.find('scripts')
    if scripts_element is None:
        raise ValueError("XML is missing required 'scripts' element.")
    for elem in scripts_element:
        list_item = ConfigScript(**elem.attrib)
        scripts.append(list_item)

    translations_element = root.find('translations')
    if translations_element is None:
        raise ValueError("XML is missing required 'translations' element.")
    for elem in translations_element:
        translation_inputs: list[str] = []

        translation_inputs_element = elem.find('translation_inputs')
        if translation_inputs_element is None:
            raise ValueError("XML is missing required 'translation_inputs' element in a translation.")
        for ti in translation_inputs_element:
            translation_inputs.append(ti.attrib['label'])
            translation_outputs: list[str] = []
            translation_outputs_element = elem.find('translation_outputs')
            if translation_outputs_element is None:
                raise ValueError("XML is missing required 'translation_outputs' element in a translation.")
            for to in translation_outputs_element:
                translation_outputs.append(to.attrib['label'])
            elem_dict = dict(elem.attrib)
            elem_dict['translation_inputs'] = translation_inputs
            elem_dict['translation_outputs'] = translation_outputs
            list_item = ConfigTranslation(**elem_dict)
            translations.append(list_item)
    module_dict = dict(root.attrib)
    module_dict['inputs'] = inputs
    module_dict['outputs'] = outputs
    module_dict['stores'] = stores
    module_dict['timers'] = timers
    module_dict['scripts'] = scripts
    module_dict['translations'] = translations
    return ConfigModule(**module_dict) """