class DecisionTree:
    class DecisionTreeNode:
        def __init__(self, left=None, right=None):
            self.left = left
            self.right = right
            return

        def get_left(self):
            return self.left

        def set_left(self, left):
            tmp = self.left
            self.left = left
            return tmp

        def get_right(self):
            return self.right

        def set_right(self, right):
            tmp = self.right
            self.right = right
            return tmp

        def is_leaf(self):
            return self.get_left() is None and self.get_right() is None

    class AttributeNode(DecisionTreeNode):
        def __init__(self, attribute):
            self.attribute = attribute
            super().__init__()
            return

        def get_attribute(self):
            return self.attribute

    class ConceptNode(DecisionTreeNode):
        def __init__(self, concept):
            self.concept = concept
            super().__init__()
            return

        def get_concept(self):
            return self.concept

            # TODO WORK ON TERMINOLOGY

    class Example:
        def __init__(self, attributes: dict, concept):
            self.attributes = attributes
            self.concept = concept
            return

        def get_concept(self):
            return self.concept

        def get_attr_value(self, attr):
            try:
                return self.attributes[attr]
            except KeyError as e:
                return None

    def __init__(self, attributes, examples):
        self._root = None
        if examples is not None:
            self._learn_tree(examples, attributes, None)
        return

    def _learn_tree(self, examples, attributes, parent_examples):
        if examples is None or len(examples) <= 0:
            return

        elif self._same_classification(examples):
            return DecisionTree.ConceptNode(examples[0].get_concept())

        else:
            curr_max = self._importance(attributes.keys()[0], examples)
            max_attr = attributes.keys()[0]
            for attr in attributes.keys():
                importance = self._importance(attr, examples)
                if importance > curr_max:
                    curr_max = importance
                    max_attr = attr

            tree = DecisionTree.AttributeNode(max_attr)

    @staticmethod
    def _importance(attribute, examples):
        # TODO Use Probability of error
        return 1.0

    @staticmethod
    def _same_classification(self, examples):
        if examples is None or len(examples) <= 0:
            return True

        concept = examples[0].get_concept()
        same_concept = True

        for example in examples:
            if example.get_concept() != concept:
                same_concept = False
                break

        return same_concept


def main():
    return


if __name__ == "__main__":
    main()
