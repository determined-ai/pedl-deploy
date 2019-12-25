class PEDLDeployment:
    def __init__(self, template, parameters):
        self._template = template
        self._parameters = parameters

    def deploy(self):
        raise NotImplementedError

    def template(self):
        return self._template

    def parameters(self):
        return self._parameters