from abc import ABC

from report_generator_module.components.parsers.base.strategy.strategy_abc import BaseParsingStrategy


class ScopeParsingStrategy(BaseParsingStrategy, ABC):
    """ Common interface for parsing scope-based lexemes """

    @property
    def current_scope_idx(self):
        return self.context.get('current_scope_idx', -1)

    @current_scope_idx.setter
    def current_scope_idx(self, new_idx: int):
        self.context['current_scope_idx'] = new_idx
