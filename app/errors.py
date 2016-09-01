

class ErrorCategory(object):

    def __init__(self, category):
        self.category = category
        self.class_name = self.make_class_name(category)
        self.types = None

    def make_class_name(self, name):
        name = name.replace(' ', '-').lower()
        return name

    def add_type(self, error_type):
        if self.types is not None:
            self.types[error_type.name] = error_type
        else:
            self.types = {
                error_type.name: error_type,
            }

    def remove_type(self, name):
        if self.types is not None and name in self.types:
            self.types.pop(name)

    def get_type(self, name):
        if self.types is not None:
            if name in self.types:
                return self.types[name]
        return None


class ErrorType(object):

    def __init__(self, name):
        """

        :return:
        """
        self.name = name
        self.class_name = self.make_class_name(name)
        self.tags = []

    def make_class_name(self, name):
        name = name.replace(' ', '-').lower()
        return name

    def set_name(self, new_name):
        self.name = new_name
        self.class_name = self.make_class_name(new_name)

    def add_tag(self, tag):
        self.tags.append(tag)