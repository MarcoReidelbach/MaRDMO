# {{ title }}

{% if Publication.Exists.1 %}
{% if 'doi' in Publication.Exists.1 %}
Workflow ID: doi:[{{ Publication.Exists.1|cut:"doi:" }}](https://doi.org/{{ Publication.Exists.1|cut:"doi:" }})
{% elif 'url' in Publication.Exists.1 %}
Workflow ID: url:[{{ Publication.Exists.1|cut:"url:" }}]({{ Publication.Exists.1|cut:"url:" }})
{% endif %}
{% else %}
Workflow ID: workflow not published
{% endif %}

## Problem Statement

{{ GeneralInformation.ProblemStatement }}    

### Object of Research and Objective

{{ GeneralInformation.ResearchObjective }}    

### Procedure

{{ GeneralInformation.Procedure }}    

### Involved Disciplines
    
**Mathematical Areas:**

{% for value in MathematicalArea.values %} {% if value %} {{ forloop.counter }} - {{ value }}  {% endif %} 
{% endfor %}

**Non-Mathematical Disciplines:**

{% for value in NonMathematicalDiscipline.values %} {% if value.mardiId != 'tbd' %} {{ forloop.counter }} - [{{ value.Name }}]({{ value.uri }}) {% endif %} {% if value.mardiId == 'tbd' %} {{ forloop.counter }} - {{ value.Name }} {% endif %}
{% endfor %}

### Data Streams
        
{% for value in GeneralInformation.DataStream.values %} {{ forloop.counter }} - {{ value }}
{% endfor %}    

## Model
        
{% for value in Models.values %} {% if value.mardiId != 'tbd' %} [{{ value.Name }}]({{ value.uri }}) ({{ value.Description }}) {% elif value.mardiId == 'tbd' %} {{ value.Name }}  ({{ value.Description}}) {% endif %}
{% endfor %}

### Discretization

{% for value in Models.values %} {% if IsTimeDiscrete in value.Properties.values %} * Time: Yes {% elif IsTimeContinuous in value.Properties.values %} * Time: No {% elif IsTimeIndependent in value.Properties.values %} * Time: Independent{% endif %} 
{% if IsSpaceDiscrete in value.Properties.values %} * Space: Yes {% elif IsSpaceContinuous in value.Properties.values %} * Space: No {% elif IsSpaceIndependent in value.Properties.values %} * Space: Independent {% endif %}
{% endfor %}

### Variables

| Name | Unit | Symbol| dependent/independent | Task |
|------|------|-------|-----------------------|------|
{% for values in Task.values %} {% for value in values.RelationQ.values %} {% if value.0 == ContainsInput or value.0 == ContainsOutput %} | {{ value.1 }} | | {{ value.2 }} | {% if ContainsInput == value.0 %} independent {% elif ContainsOutput == value.0 %} dependent {% endif %} | {{ values.Name }} | {% endif %} 
{% endfor %} {% endfor %}

### Parameters

| Name | Unit | Symbol | Task |
|------|------|--------|------|
{% for values in Task.values %} {% for value in values.RelationQ.values %} {% if value.0 == ContainsParameter %} | {{value.1 }} | | {{ value.2 }} | {{ values.Name }} {% endif %}
{% endfor %} {% endfor %}

## Process Information

### Process Steps

| Name | Description | Input | Output | Method | Parameter | Environment | Mathematical Area |
|------|-------------|-------|--------|--------|-----------|-------------|-------------------|
{% for values in ProcessStep.values %} | {{ values.Name }} | {{ values.Description }} | {% for input in values.Input.values %} {{ input }} {% if not forloop.last %}, {% endif %} {% endfor %} | {% for output in values.Output.values %} {{ output }} {% if not forloop.last %}, {% endif %} {% endfor %} | {% for method in values.Method.values %} {{ method }} {% if not forloop.last %}, {% endif %} {% endfor %} | {{ values.Parameter }} | {% for environment in values.Environment.values %} {{ environment }} {% if not forloop.last %}, {% endif %} {% endfor %} | {% for matharea in values.MathArea.values %} {{ matharea }} {% if not forloop.last %}, {% endif %} {% endfor %} |
{% endfor %}

### Applied Methods

| ID | Name | Process Step | Parameter | implemented by |
|----|------|--------------|-----------|----------------|
{% for values in Method.values %} | {% if values.mardiId != 'tbd' %} mardi:[{{ values.mardiId }}]({{ values.uri }}) {% elif values.mardiId == 'tbd' %} mardi:{{ values.mardiId }} {% endif %} | {{ values.Name }} | {% for processstep in values.ProcessStep.values %} {{ processstep }} {% if not forloop.last %}, {% endif %} {% endfor %} | {{ values.Parameter }} | {% for software in values.Software.values %} {{ software }} {% if not forloop.last %}, {% endif %} {% endfor %} |
{% endfor %}

### Software used

| ID | Name | Description | Version | Programming Language | Dependencies | versioned | published | documented |
|----|------|-------------|---------|----------------------|--------------|-----------|-----------|------------|
{% for values in Software.values %} | {% if values.mardiId != 'tbd' %} mardi:[{{ values.mardiId }}]({{ values.uri }}) {% elif values.mardiId == 'tbd' %} mardi:{{ values.mardiId }} {% endif %} | {{ values.Name }} | {{ values.Description }} | {{ values.Version }} | {% for subproperty in values.SubProperty.values %} {% if subproperty.mardiId != 'tbd' %} [{{ subproperty.Name }}]({{ subproperty.uri }}) {% elif subproperty.mardiId == 'tbd' %} {{ subproperty.Name }} {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %} | {% for dependency in values.Dependency.values %} {{ dependency }} {% if not forloop.last %}, {% endif %} {% endfor %} | {% if values.Versioned.0 == YesText %} [Yes]({{values.Versioned.1}}) {% elif values.Versioned.0 != YesText %} No {% endif %} | {% if values.Published.0 == YesText %} [Yes]({{values.Published.1}}) {% elif values.Published.0 != YesText %} No {% endif %} | {% if values.Documented.0 == YesText %} [Yes]({{values.Documented.1}}) {% elif values.Documented.0 != YesText %} No {% endif %} |
{% endfor %}

{% if Settings.WorkflowType == Computation %}  
### Hardware

| ID | Name | Processor | Compiler | #Nodes | #Cores |
|----|------|-----------|----------|--------|--------|
{% for values in Hardware.values %} | {% if values.mardiId != 'tbd' %} mardi:[{{ values.mardiId }}]({{ values.uri }}) {% elif values.mardiId == 'tbd' %} mardi:{{ values.mardiId }} {% endif %} | {{ values.Name }} | {% for subproperty in values.SubProperty.values %} {% if subproperty.mardiId != 'tbd' %} [{{ subproperty.Name }}]({{ subproperty.uri }}) {% elif subproperty.mardiId == 'tbd' %} {{ subproperty.Name }} {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %} | {% for subproperty2 in values.SubProperty2.values %} {% if subproperty2.mardiId != 'tbd' %} [{{ subproperty2.Name }}]({{ subproperty2.uri }}) {% elif subproperty2.mardiId == 'tbd' %} {{ subproperty2.Name }} {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %} | {{ values.Node }} | {{ values.Core }} |
{% endfor %}
{% endif %}

{% if Settings.WorkflowType == Analysis %}
### Experimental Devices

| ID | Name | Description | Version | Part Number | Serial Number | Location | Software|
|----|------|-------------|---------|-------------|---------------|----------|---------|
{% for values in ExperimentalDevice.values %} | {% if values.mardiId != 'tbd' %} mardi:[{{ values.mardiId }}]({{ values.uri }}) {% elif values.mardiId == 'tbd' %} mardi:{{ values.mardiId }} {% endif %} | {{ values.Name }} | {{ values.Description }} | {{ values.Version }} | {{ values.PartNumber }} | {{ values.SerialNumber }} | {% for subproperty in values.SubProperty.values %} {% if subproperty.mardiId != 'tbd' %} [{{ subproperty.Name }}]({{ subproperty.uri }}) {% elif subproperty.mardiId == 'tbd' %} {{ subproperty.Name }} {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %} | {% for subproperty2 in values.SubProperty2.values %} {% if subproperty2.mardiId != 'tbd' %} [{{ subproperty2.Name }}]({{ subproperty2.uri }}) {% elif subproperty2.mardiId == 'tbd' %} {{ subproperty2.Name }} {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %} |
{% endfor %}
{% endif %}

### Input Data

| ID | Name | Size | Data Structure | Format Representation | Format Exchange | binary/text | proprietary | to publish | to archive |
|----|------|------|----------------|-----------------------|-----------------|-------------|-------------|------------|------------|
{% for values in DataSet.values %} {% if 'Input' in values.Type.values %} | {% if values.mardiId != 'tbd' %} mardi:[{{ values.mardiId }}]({{ values.uri }}) {% elif values.mardiId == 'tbd' %} mardi:{{ values.mardiId }} {% endif %} | {{ values.Name }} | {% if values.Size == Small %} Small (KB - MB) {% elif values.Size == Medium %} Medium (MB - GB) {% elif values.Size == Large %} Large (GB - TB) {% elif value.Size == VeryLarge %} Very Large (>TB) {% endif %} | {{ values.DataStructure }} | {{ values.RepresentationFormat }} | {{ values.ExchangeFormat }} | {% if values.BinaryText == Binary %} Binary {% elif values.BinaryText == Text %} Text {% endif %} | {% if values.Proprietary == Yes %} Yes {% elif values.Proprietary == No %} No {% endif %} | {% if values.Publication == Yes %} Yes {% elif values.Publication == No %} No {% endif %} | {% if values.Archiving.0 == YesText %} {{ values.Archiving.1 }} {% elif values.Archiving.0 == NoText %} No {% endif %} | {% endif %}
{% endfor %}

### Output Data

| ID | Name | Size | Data Structure | Format Representation | Format Exchange | binary/text | proprietary | to publish | to archive |
|----|------|------|----------------|-----------------------|-----------------|-------------|-------------|------------|------------|
{% for values in DataSet.values %} {% if 'Output' in values.Type.values %} | {% if values.mardiId != 'tbd' %} mardi:[{{ values.mardiId }}]({{ values.uri }}) {% elif values.mardiId == 'tbd' %} mardi:{{ values.mardiId }} {% endif %} | {{ values.Name }} | {% if values.Size == Small %} Small (KB - MB) {% elif values.Size == Medium %} Medium (MB - GB) {% elif values.Size == Large %} Large (GB - TB) {% elif value.Size == VeryLarge %} Very Large (>TB) {% endif %} | {{ values.DataStructure }} | {{ values.RepresentationFormat }} | {{ values.ExchangeFormat }} | {% if values.BinaryText == Binary %} Binary {% elif values.BinaryText == Text %} Text {% endif %} | {% if values.Proprietary == Yes %} Yes {% elif values.Proprietary == No %} No {% endif %} | {% if values.Publication == Yes %} Yes {% elif values.Publication == No %} No {% endif %} | {% if values.Archiving.0 == YesText %} {{ values.Archiving.1 }} {% elif values.Archiving.0 == NoText %} No {% endif %} | {% endif %}
{% endfor %}
                                                           
## Reproducibility

{% if Settings.WorkflowType == Computation %}
### Mathematical Reproducibility
{% if ReproducibilityComputational.Mathematically == Yes %}
Yes: {{ ReproducibilityComputational.MathematicallyInfo }}
{% elif ReproducibilityComputational.Mathematically == No %}
No
{% endif %}
### Runtime Reproducibility
{% if ReproducibilityComputational.Runtime == Yes %}
Yes: {{ ReproducibilityComputational.RuntimeInfo }}
{% elif ReproducibilityComputational.Runtime == No %}
No
{% endif %}
### Reproducibility of Results
{% if ReproducibilityComputational.Result == Yes %}
Yes: {{ ReproducibilityComputational.ResultInfo }}
{% elif ReproducibilityComputational.Result == No %}
No
{% endif %}
{% endif %}
### Reproducibility on original {% if Settings.WorkflowType == Computation %}Hardware{% elif Settings.WorkflowType == Analysis %}Devices/Instruments/Hardware{% endif %}
{% if ReproducibilityComputational.OriginalHardware == Yes %}
Yes: {{ ReproducibilityComputational.OriginalHardwareInfo }}
{% elif ReproducibilityComputational.OriginalHardware == No %}
No
{% endif %}
###Reproducibility on other {% if Settings.WorkflowType == Computation %}Hardware{% elif Settings.WorkflowType == Analysis %}Devices/Instruments/Hardware{% endif %}
{% if ReproducibilityComputational.OtherHardware == Yes %}
Yes: {{ ReproducibilityComputational.OtherHardwareInfo }}
{% elif ReproducibilityComputational.OtherHardware == No %}
No
{% endif %}
### Transferability to
{% for value in ReproducibilityComputational.Transferability.values %}
{{ value }}
{% if not forloop.last %}<br>{% endif %}
{% endfor %}


## Legend
The following abbreviations are used in the document to indicate/resolve IDs:
doi: DOI / https://dx.doi.org/
sw: swMATH / https://swmath.org/software/
wikidata: https://www.wikidata.org/wiki/
mardi: https://portal.mardi4nfdi.de/wiki/

