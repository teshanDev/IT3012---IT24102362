class KnowledgeBase:
    def __init__(self):
        # Set to store unique string facts
        self.facts = set()
        # List of tuples: (list_of_premises, conclusion_string)
        self.rules = []

    def tell_fact(self, fact_string: str):
        """Adds an observed fact into the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list: list, conclusion_string: str):
        """Adds a Horn Clause rule (premises -> conclusion) into the KB."""
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        """Clears current working memory/percepts while preserving rules."""
        self.facts.clear()

    def forward_chain(self):
        """
        Data-driven Forward Chaining algorithm.
        Repeatedly applies Generalized Modus Ponens until a fixed point is reached.
        """
        new_facts_added = True
        while new_facts_added:
            new_facts_added = False
            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    # Modus Ponens check: are all premises satisfied in facts?
                    if all(p in self.facts for p in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True