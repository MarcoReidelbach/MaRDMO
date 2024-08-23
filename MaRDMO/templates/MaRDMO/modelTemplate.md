# Title: {{ title }}

**Authors**:

- **family-names**: {{ Creator.Surname }}  
  **given-names**: {{ Creator.GivenName }}  
  {% for id in Creator.orcidID %} **orcid**:{{ id }}
  {% endfor %}
  {% for id in Creator.zbmathID %} **zbmath**:{{ id }}
  {% endfor %}
  **Date-Released**: YYYY-MM-DD  
  **Version**: Major.Minor.Patch

{% for values in MathematicalModel.values %}

# Mathematical Model MM{{ forloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }} 
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}  
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %} 
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %}
**Wikipedia**: {{ values.Reference }}
**Properties**: {% for value in values.Properties.values %} {% if value == IsConvex %} Is Convex {% elif value == IsNotConvex %} Is Not Convex {% elif value == IsDeterministic %} Is Deterministic {% elif value == IsStochastic %} Is Stochastic {% elif value == IsDimensionless %} Is Dimensionless {% elif value == IsDimensional %} Is Dimensional {% elif value == IsDynamic %} Is Dynamic {% elif value == IsStatic %} Is Static {% elif value == IsLinear %} Is Linear {% elif value == IsNotLinear %} Is Not Linear {% elif value == IsSpaceContinuous %} Is Space-Continuous {% elif value == IsSpaceDiscrete %} Is Space-Discrete {% elif value == IsSpaceIndependent %} Is Space-Independent {% elif value == IsTimeContinuous %} Is Time-Continuous {% elif value == IsTimeDiscrete %} Is Time-Discrete {% elif value == IsTimeIndependent %} Is Time-Independent {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %}   

{% for models in values.RelationRP1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Research Problems**:

{% endif %}

models: {{ models }} 

{% endfor %}

{% for relation in values.RelationMM1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Mathematical Models**:

{% endif %}

{% if relation.0 == GeneralizedBy %} generalized by Model: {{relation.1 }}
{% elif relation.0 == Generalizes %} generalizes Model: {{relation.1 }}
{% elif relation.0 == DiscretizedBy %} discretized by Model: {{relation.1 }}
{% elif relation.0 == Discretizes %} discretizes Model: {{relation.1 }}
{% elif relation.0 == ContainedIn %} contained in Model: {{relation.1 }}
{% elif relation.0 == Contains %} contains Model: {{relation.1 }}
{% elif relation.0 == ApproximatedBy %} approximated by Model: {{relation.1 }}
{% elif relation.0 == Approximates %} approximates Model: {{relation.1 }}
{% elif relation.0 == LinearizedBy %} linearized by Model: {{relation.1 }}
{% elif relation.0 == Linearizes %} linearizes Model: {{relation.1 }}
{% elif relation.0 == SimilarTo %} similar to Model: {{relation.1 }}
{% endif %}
{% endfor %}

## List of Mathematical Formulations

{% for values in MathematicalFormulation.values %}
{% for models in values.RelationMM1.values %}
{% if models.1 == forloop.parentloop.parentloop.counter %}

### F{{ forloop.parentloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }}
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %}
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %}

&nbsp;

**Defining formulations**: {%for value in values.Formula.values %} {{ value }} {% if not forloop.last %}, {% endif %} {% endfor %}

&nbsp;

| Symbol | Quantity | Quantity Id | Quantity Kind | Quant. Kind Id | Description | 
|:------:|:--------:|:-----------:|:-------------:|:--------------:|:-----------:|
{% for value in values.Element.values %} | {{ value.Symbol }} | {% if value.Info %} {{ value.Info.Name }} {% else %} {{ value.Quantity }} {% endif %} | {{ value.Info.QID }} | {{ value.Info.QKName }} | {{ value.Info.QKID }} | {{ value.Info.Description }} |   
{% endfor %}

&nbsp;

**Properties**:{% for value in values.Properties.values %} {% if value == IsConvex %} Is Convex {% elif value == IsNotConvex %} Is Not Convex {% elif value == IsDeterministic %} Is Deterministic {% elif value == IsStochastic %} Is Stochastic {% elif value == IsDimensionless %} Is Dimensionless {% elif value == IsDimensional %} Is Dimensional {% elif value == IsDynamic %} Is Dynamic {% elif value == IsStatic %} Is Static {% elif value == IsLinear %} Is Linear {% elif value == IsNotLinear %} Is Not Linear {% elif value == IsSpaceContinuous %} Is Space-Continuous {% elif value == IsSpaceDiscrete %} Is Space-Discrete {% elif value == IsSpaceIndependent %} Is Space-Independent {% elif value == IsTimeContinuous %} Is Time-Continuous {% elif value == IsTimeDiscrete %} Is Time-Discrete {% elif value == IsTimeIndependent %} Is Time-Independent {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %}

{% for values in values.RelationMM1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Mathematical Models**: 

{% endif %}

{%if values.0 == ContainedAsAssumptionIn %} contained as Assumption in: {{ values.2 }}
{% elif values.0 == ContainedAsBoundaryConditionIn %} contained as Boundary Condition in: {{ values.2 }} 
{% elif values.0 == ContainedAsConstraintConditionIn %} contained as Constraint Condition in: {{ values.2 }} 
{% elif values.0 == ContainedAsDefintionIn %} contained as Defintion in: {{ values.2 }} 
{% elif values.0 == ContainedAsFormulationIn %} contained as Formulation in: {{ values.2 }} 
{% elif values.0 == ContainedAsInitialConditionIn %} contained as Initial Condition in: {{ values.2 }} 
{% elif values.0 == ContainedAsFinalConditionIn %} contained as Final Condition in: {{ values.2 }}
{% endif %} 
{% endfor %}

{% for values in values.RelationMF1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to other Mathematical Formulations I**:

{% endif %}

{% if values.0 == ContainsAssumption %} contains as Assumption: {{ values.1 }}
{% elif values.0 == ContainedAsAssumptionIn %} contained as Assumption in: {{ values.1 }}
{% elif values.0 == ContainsBoundaryCondition %} contains as Boundary Condition: {{ values.1 }}
{% elif values.0 == ContainedAsBoundaryConditionIn %} contained as Boundary Condition in: {{ values.1 }} 
{% elif values.0 == ContainsConstraintCondition %} contains as Constraint Condition: {{ values.1 }}
{% elif values.0 == ContainedAsConstraintConditionIn %} contained as Constraint Condition in: {{ values.1 }} 
{% elif values.0 == ContainsCouplingCondition %} contains as Coupling Condition: {{ values.1 }}
{% elif values.0 == ContainedAsCouplingConditionIn %} contained as Coupling Condition in: {{ values.1 }} 
{% elif values.0 == ContainsFormulation %} contains as Formulation: {{ values.1 }}
{% elif values.0 == ContainedAsFormulationIn %} contained as Formulation in: {{ values.1 }} 
{% elif values.0 == ContainsInitialCondition %} contains as Initial Condition: {{ values.1 }}
{% elif values.0 == ContainedAsInitialConditionIn %} contained as Initial Condition in: {{ values.1 }} 
{% elif values.0 == ContainsFinalCondition %} contains as Final Condition: {{ values.1 }}
{% elif values.0 == ContainedAsFinalConditionIn %} contained as Final Condition in: {{ values.1 }}
{% endif %} 
{% endfor %}

{% for values in values.RelationMF2.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to other Mathematical Formulations II**:

{% endif %}

{% if values.0 == ApproximatedBy %} approximated by Formulation: {{ values.1 }}
{% elif values.0 == Approximates %} approximates Formulation: {{ values.1 }}
{% elif values.0 == DiscretizedBy %} discretized by Formulation: {{ values.1 }}
{% elif values.0 == Discretizes %} discretizes Formulation: {{ values.1 }}
{% elif values.0 == GeneralizedBy %} generalized by Formulation: {{ values.1 }}
{% elif values.0 == Generalizes %} generalizes Formulation: {{ values.1 }}
{% elif values.0 == NondimensionalizedBy %} nondimensionalized by Formulation: {{ values.1 }}
{% elif values.0 == Nondimensionalzes %} nondimensionalizes Formulation: {{ values.1 }}
{% elif values.0 == LinearizedBy %} linearized by Formulation: {{ values.1 }}
{% elif values.0 == Linearizes %} linearizes Formulation: {{ values.1 }}
{% elif values.0 == SimilarTo %} similar to Formulation: {{ values.1 }}
{% endif %}
{% endfor %}

{% endif %}
{% endfor %}
{% endfor %}
{% endfor %}

# Task

{% for values in Task.values %}

## Task T{{ forloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }}
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}  
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %}
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %} 
**Wikipedia**: {{ values.Reference }}
**Properties**: {% for value in values.Properties.values %} {% if value == IsLinear %} Is Linear {% elif value == IsNotLinear %} Is Not Linear {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %}  
**Task Type**: {% for value in values.TaskClass.values %} {% if value == ComputationalTask %} Computational Task {% endif %} {% endfor %}

{% for value in values.RelationMM.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Mathematical Models**

{% endif %}

applies Mathematical Model: {{ value }}

{% endfor %}

{% for value in values.RelationQQK.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Quantities / Quantity Kinds**

{% endif %}

{% if value.0 == ContainsInput %} contains Input: {{ value.1 }}
{% elif value.0 == ContainsOutput %} contains Output: {{ value.1 }}
{% elif value.0 == ContainsObjective %} contains Objective: {{ value.1 }}
{% elif value.0 == ContainsParameter %} contains Parameter: {{ value.1 }}
{% elif value.0 == ContainsConstant %} contains Constant: {{ value.1 }}
{% endif %}
{% endfor %}

{% for value in values.RelationT.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Tasks**

{% endif %}

{% if value.0 == GeneralizedBy %} generalized by Task: {{ value.1 }}
{% elif value.0 == Generalizes %} generalizes Task: {{ value.1 }}
{% elif value.0 == DiscretizedBy %} discretized by Task: {{ value.1 }}
{% elif value.0 == Discretizes %} discretizes Task: {{ value.1 }}
{% elif value.0 == ContainedIn %} contained in Task: {{ value.1 }}
{% elif value.0 == Contains %} contains Task: {{ value.1 }}
{% elif value.0 == ApproximatedBy %} approximated by Task: {{ value.1 }}
{% elif value.0 == Approximates %} approximates Task: {{ value.1 }}
{% elif value.0 == LinearizedBy %} linearized by Task: {{ value.1 }}
{% elif value.0 == Linearizes %} linearizes Task: {{ value.1 }}
{% elif value.0 == SimilarTo %} similar to Task: {{ value.1 }}
{% endif %}
{% endfor %}

## List of Mathematical Formulations

{% for values in MathematicalFormulation.values %}
{% for tasks in values.RelationT1.values %}
{% if tasks.1 == forloop.parentloop.parentloop.counter %}

### F{{ forloop.parentloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }}
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %}
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %}

&nbsp;

**Defining formulations**: {%for value in values.Formula.values %} {{ value }} {% if not forloop.last %}, {% endif %} {% endfor %}

&nbsp;

| Symbol | Quantity | Quantity Id | Quantity Kind | Quant. Kind Id | Description |
|:------:|:--------:|:-----------:|:-------------:|:--------------:|:-----------:|
{% for value in values.Element.values %} | {{ value.Symbol }} | {% if value.Info %} {{ value.Info.Name }} {% else %} {{ value.Quantity }} {% endif %} | {{ value.Info.QID }} | {{ value.Info.QKName }} | {{ value.Info.QKID }} | {{ value.Info.Description }} |
{% endfor %}

&nbsp;

**Properties**:{% for value in values.Properties.values %} {% if value == IsConvex %} Is Convex {% elif value == IsNotConvex %} Is Not Convex {% elif value == IsDeterministic %} Is Deterministic {% elif value == IsStochastic %} Is Stochastic {% elif value == IsDimensionless %} Is Dimensionless {% elif value == IsDimensional %} Is Dimensional {% elif value == IsDynamic %} Is Dynamic {% elif value == IsStatic %} Is Static {% elif value == IsLinear %} Is Linear {% elif value == IsNotLinear %} Is Not Linear {% elif value == IsSpaceContinuous %} Is Space-Continuous {% elif value == IsSpaceDiscrete %} Is Space-Discrete {% elif value == IsSpaceIndependent %} Is Space-Independent {% elif value == IsTimeContinuous %} Is Time-Continuous {% elif value == IsTimeDiscrete %} Is Time-Discrete {% elif value == IsTimeIndependent %} Is Time-Independent {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %}

{% for values in values.RelationT1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Tasks**:

{% endif %}

{% if values.0 == ContainedAsAssumptionIn %} contained as Assumption in: {{ values.2 }}
{% elif values.0 == ContainedAsBoundaryConditionIn %} contained as Boundary Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsConstraintConditionIn %} contained as Constraint Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsDefinitionIn %} contained as Definition in: {{ values.2 }}
{% elif values.0 == ContainedAsFormulationIn %} contained as Formulation in: {{ values.2 }}
{% elif values.0 == ContainedAsInitialConditionIn %} contained as Initial Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsFinalConditionIn %} contained as Final Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsInputIn %} contained as Input in: {{ values.2 }}
{% elif values.0 == ContainedAsOutputIn %} contained as Output in: {{ values.2 }}
{% elif values.0 == ContainedAsObjectiveIn %} contained as Objective in: {{ values.2 }}
{% elif values.0 == ContainedAsParameterIn %} contained as Parameter in: {{ values.2 }}
{% endif %}
{% endfor %}


{% for values in values.RelationMM1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Mathematical Models**:

{% endif %}

{%if values.0 == ContainedAsAssumptionIn %} contained as Assumption in: {{ values.2 }}
{% elif values.0 == ContainedAsBoundaryConditionIn %} contained as Boundary Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsConstraintConditionIn %} contained as Constraint Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsDefintionIn %} contained as Defintion in: {{ values.2 }}
{% elif values.0 == ContainedAsFormulationIn %} contained as Formulation in: {{ values.2 }}
{% elif values.0 == ContainedAsInitialConditionIn %} contained as Initial Condition in: {{ values.2 }}
{% elif values.0 == ContainedAsFinalConditionIn %} contained as Final Condition in: {{ values.2 }}
{% endif %}
{% endfor %}

{% for values in values.RelationMF1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to other Mathematical Formulations I**:

{% endif %}

{% if values.0 == ContainsAssumption %} contains as Assumption: {{ values.1 }}
{% elif values.0 == ContainedAsAssumptionIn %} contained as Assumption in: {{ values.1 }}
{% elif values.0 == ContainsBoundaryCondition %} contains as Boundary Condition: {{ values.1 }}
{% elif values.0 == ContainedAsBoundaryConditionIn %} contained as Boundary Condition in: {{ values.1 }}
{% elif values.0 == ContainsConstraintCondition %} contains as Constraint Condition: {{ values.1 }}
{% elif values.0 == ContainedAsConstraintConditionIn %} contained as Constraint Condition in: {{ values.1 }}
{% elif values.0 == ContainsCouplingCondition %} contains as Coupling Condition: {{ values.1 }}
{% elif values.0 == ContainedAsCouplingConditionIn %} contained as Coupling Condition in: {{ values.1 }}
{% elif values.0 == ContainsFormulation %} contains as Formulation: {{ values.1 }}
{% elif values.0 == ContainedAsFormulationIn %} contained as Formulation in: {{ values.1 }}
{% elif values.0 == ContainsInitialCondition %} contains as Initial Condition: {{ values.1 }}
{% elif values.0 == ContainedAsInitialConditionIn %} contained as Initial Condition in: {{ values.1 }}
{% elif values.0 == ContainsFinalCondition %} contains as Final Condition: {{ values.1 }}
{% elif values.0 == ContainedAsFinalConditionIn %} contained as Final Condition in: {{ values.1 }}
{% endif %}
{% endfor %}

{% for values in values.RelationMF2.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to other Mathematical Formulations II**:

{% endif %}

{% if values.0 == ApproximatedBy %} approximated by Formulation: {{ values.1 }}
{% elif values.0 == Approximates %} approximates Formulation: {{ values.1 }}
{% elif values.0 == DiscretizedBy %} discretized by Formulation: {{ values.1 }}
{% elif values.0 == Discretizes %} discretizes Formulation: {{ values.1 }}
{% elif values.0 == GeneralizedBy %} generalized by Formulation: {{ values.1 }}
{% elif values.0 == Generalizes %} generalizes Formulation: {{ values.1 }}
{% elif values.0 == NondimensionalizedBy %} nondimensionalized by Formulation: {{ values.1 }}
{% elif values.0 == Nondimensionalzes %} nondimensionalizes Formulation: {{ values.1 }}
{% elif values.0 == LinearizedBy %} linearized by Formulation: {{ values.1 }}
{% elif values.0 == Linearizes %} linearizes Formulation: {{ values.1 }}
{% elif values.0 == SimilarTo %} similar to Formulation: {{ values.1 }}
{% endif %}
{% endfor %}

{% endif %}
{% endfor %}
{% endfor %}

{% endfor %}

# Publication

{% for values in PublicationModel.values %}

## P{{ forloop.counter }}: {{ values.Name }}

MathModID:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}
DOI:{% if 'doi' in values.Reference %} {{ values.Reference|cut:"doi:" }} {% endif %}   
URL:{% if 'url' in values.Reference %} {{ values.Reference|cut:"url:" }} {% endif %}  

{% for values in values.RelationP.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Entities of the Mathematical Model(s)**:

{% endif %}

{% if values.0 == Documents %} documents: {{ values.1 }}
{% elif values.0 == Invents %} invents: {{ values.1 }}
{% elif values.0 == Studies %} studies: {{ values.1 }}
{% elif values.0 == Surveys %} surveys: {{ values.1 }}
{% elif values.0 == Uses %} uses: {{ values.1 }}
{% endif %}
{% endfor %}
{% endfor %}

# Research Field

{% for values in ResearchField.values %}

## RF{{ forloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }}
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %} 
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %}   
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %}

{% for relation in values.RelationRF1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to other Research Fields**:

{% endif %}

{% if relation.0 == GeneralizedBy %} generalized by Field: {{relation.1 }} 
{% elif relation.0 == Generalizes %} generalizes Field: {{relation.1 }}
{% elif relation.0 == SimilarTo %} similar to Field: {{relation.1 }}
{% endif %}
{% endfor %} 

{% endfor %}

# Research Problem

{% for values in ResearchProblem.values %}

## RP{{ forloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }}
**DOI**:{{ values.Reference|cut:"doi:" }}  
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %} 
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %} 

{% for researchfield in values.RelationRF1.values %}
{% if forloop.counter == 1 %}

&nbsp;

**Relations to Research Fields**:

{% endif %}

contained in Field: {{ researchfield }}
{% endfor %}

{% for relation in values.RelationRP1.values %}
{% if forloop.counter == 1 %}
&nbsp;

**Relations to other Research Problems**:

{% endif %}

{% if relation.0 == GeneralizedBy %} generalized by Problem: {{relation.1 }}
{% elif relation.0 == Generalizes %} generalizes Problem: {{relation.1 }}
{% elif relation.0 == SimilarTo %} similar to Problem: {{relation.1 }}
{% endif %}
{% endfor %}

{% endfor %}

# Quantity / Quantity Kind

{% for values in Quantity.values %}

## QQK{{ forloop.counter }}: {{ values.Name }}

**Description**: {{ values.Description }}
**Class**: {% if values.QorQK == QuantityClass %} Quantity {% elif values.QorQK == QuantityKindClass %} Quantity Kind {% endif %} 
**DOI**:{% if 'doi' in values.ID %} {{ values.ID|cut:"doi:" }} {% endif %}
**MathModDB**:{% if values.MathModID and values.MathModID != 'not in MathModDB' %} {{ values.MathModID }} {% endif %}
**WikiData**:{% if 'wikidata' in values.ID %} {{ values.ID|cut:"wikidata:" }} {% endif %}
**MaRDI**:{% if 'mardi' in values.ID %} {{ values.ID|cut:"mardi:" }} {% endif %}
**Properties**: {% if values.Properties %} {% for value in values.Properties.values %} {% if value == IsDimensionless %} Is Dimensionless {% elif value == IsDimensional %} Is Dimensional {% elif value == IsLinear %} Is Linear {% elif value == IsNotLinear %} Is Not Linear {% endif %} {% if not forloop.last %}, {% endif %}{% endfor %} {% endif %}

{% if values.QorQK == QuantityClass %}

{% for values in values.RelationQQ.values %}
{% if forloop.counter == 1 %}
&nbsp;

**Relations to other Quantities**:

{% endif %}

{% if values.0 == GeneralizedBy %} generalized by Quantity: {{ values.1 }}
{% elif values.0 == Generalizes %} generalizes Quantity: {{ values.1 }}
{% elif values.0 == ApproximatedBy %} approximated by Quantity: {{ values.1 }}
{% elif values.0 == Approximates %} approximates Quantity: {{ values.1 }}
{% elif values.0 == LinearizedBy %} linearized by Quantity: {{ values.1 }}
{% elif values.0 == Linearizes %} linearizes Quantity: {{ values.1 }}
{% elif values.0 == NondimensionalizedBy %} nondimensionalized by Quantity: {{ values.1 }}
{% elif values.0 == Nondimensionalizes %} nondimensionalizes Quantity: {{ values.1 }}
{% elif values.0 == SimilarTo %} similar to Quantity: {{ values.1 }}
{% endif %}
{% endfor %}

{% for values in values.RelationQQK.values %}
{% if forloop.counter == 1 %}
&nbsp;

**Relations to Quantity Kinds**:

{% endif %}

{% if values.0 == GeneralizedBy %} generalized by Quantity Kind: {{ values.1 }}
{% elif values.0 == Generalizes %} generalizes Quantity Kind: {{ values.1 }}
{% elif values.0 == NondimensionalizedBy %} nondimensionalized by Quantity Kind: {{ values.1 }}
{% elif values.0 == Nondimensionalizes %} nondimensionalizes Quantity Kind: {{ values.1 }}
{% elif values.0 == SimilarTo %} similar to Quantity Kind: {{ values.1 }}
{% endif %}
{% endfor %}

{% if values.MDef %}

#Definition

**Name**: {{ values.MDef.Name }}
**Description**: {{ values.MDef.Description }}
**MathModDB**:{% if values.MDef.MathModID and values.MDef.MathModID != 'not in MathModDB' %} {{ values.MDef.MathModID }} {% endif %}
**WikiData**:{% if 'wikidata' in values.MDef.ID %} {{ values.MDef.ID|cut:"wikidata:" }} {% endif %}
**MaRDI**:{% if 'mardi' in values.MDef.ID %} {{ values.MDef.ID|cut:"mardi:" }} {% endif %}

&nbsp;

**Defining formulations**: {%for value in values.MDef.Formula.values %} {{ value }} {% if not forloop.last %}, {% endif %} {% endfor %}

&nbsp;

| Symbol | Quantity | Quantity Id | Quantity Kind | Quant. Kind Id | Description |
|:------:|:--------:|:-----------:|:-------------:|:--------------:|:-----------:|
{% for value in values.MDef.Element.values %} | {{ value.Symbol }} | {% if value.Info %} {{ value.Info.Name }} {% else %} {{ value.Quantity }} {% endif %} | {{ value.Info.QID }} | {{ value.Info.QKName }} | {{ value.Info.QKID }} | {{ value.Info.Description }} |
{% endfor %}

&nbsp;

**Properties**:{% for value in values.Properties.values %} {% if value == IsConvex %} Is Convex {% elif value == IsNotConvex %} Is Not Convex {% elif value == IsDeterministic %} Is Deterministic {% elif value == IsStochastic %} Is Stochastic {% elif value == IsDimensionless %} Is Dimensionless {% elif value == IsDimensional %} Is Dimensional {% elif value == IsDynamic %} Is Dynamic {% elif value == IsStatic %} Is Static {% elif value == IsLinear %} Is Linear {% elif value == IsNotLinear %} Is Not Linear {% elif value == IsSpaceContinuous %} Is Space-Continuous {% elif value == IsSpaceDiscrete %} Is Space-Discrete {% elif value == IsSpaceIndependent %} Is Space-Independent {% elif value == IsTimeContinuous %} Is Time-Continuous {% elif value == IsTimeDiscrete %} Is Time-Discrete {% elif value == IsTimeIndependent %} Is Time-Independent {% endif %} {% if not forloop.last %}, {% endif %} {% endfor %}

{% endif %}

{% elif values.QorQK == QuantityKindClass %}

{% for values in values.RelationQKQK.values %}
{% if forloop.counter == 1 %}
&nbsp;

**Relations to other Quantity Kinds**:

{% endif %}

{% if values.0 == GeneralizedBy %} generalized by Quantity Kind: {{ values.1 }}
{% elif values.0 == Generalizes %} generalizes Quantity Kind: {{ values.1 }}
{% elif values.0 == NondimensionalizedBy %} nondimensionalized by Quantity Kind: {{ values.1 }}
{% elif values.0 == Nondimensionalizes %} nondimensionalizes Quantity Kind: {{ values.1 }}
{% elif values.0 == SimilarTo %} similar to Quantity Kind: {{ values.1 }}
{% endif %}
{% endfor %}

{% for values in values.RelationQKQ.values %}
{% if forloop.counter == 1 %}
&nbsp;

**Relations to Quantities**:

{% endif %}

{% if values.0 == GeneralizedBy %} generalized by Quantity: {{ values.1 }}
{% elif values.0 == Generalizes %} generalizes Quantity: {{ values.1 }}
{% elif values.0 == NondimensionalizedBy %} nondimensionalized by Quantity: {{ values.1 }}
{% elif values.0 == Nondimensionalizes %} nondimensionalizes Quantity: {{ values.1 }}
{% elif values.0 == SimilarTo %} similar to Quantity: {{ values.1 }}
{% endif %}
{% endfor %}

{% endif %}
{% endfor %}
