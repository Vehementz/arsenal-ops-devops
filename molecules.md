Here’s your Molecule guide, mimicking the structured and concise style you've used for Helm:

# Molecule

Molecule is a testing framework for Ansible roles and playbooks. It helps automate the process of testing, linting, and validating Ansible code in isolated environments.

#platform/multiple #target/Ansible #cat/DevOps

% molecule, ansible, testing, validation

## Molecule - Initialize a Role

Initialize a new Molecule scenario for testing an Ansible role.

```
molecule init
```

## Molecule - Initialize a Scenario

Create a new testing scenario within an existing Molecule setup.

```
molecule init scenario
```

## Molecule - List Scenarios

Display the current Molecule scenarios and their configurations.

```
molecule list
```

## Molecule - Log in to an Instance

Access a running instance created by Molecule for testing.

```
molecule login
```

## Molecule - Display the Test Matrix

Show the ordered list of actions that Molecule will execute in the test sequence.

```
molecule matrix
```

## Molecule - Create Instances

Create the instances defined in the Molecule scenario.

```
molecule create
```

## Molecule - Test Role on an Instance

Run the role or playbook on the created instance to verify functionality.

```
molecule converge
```

## Molecule - Destroy Instances

Tear down and clean up all the instances created by the Molecule scenario.

```
molecule destroy
```

## Molecule - Verify Instance Creation

List and check if the instances created by Molecule are running.

```
molecule list
```

## Molecule - Manually Inspect an Instance

Log in to an instance for manual inspection or debugging after running tests.

```
molecule login
```

