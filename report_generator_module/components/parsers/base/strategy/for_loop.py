import logging

from report_generator_module.components.grammar.base_grammar import BaseGrammar
from report_generator_module.components.parsers.base.strategy.scopable import ScopeParsingStrategy
from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value

logger = logging.getLogger(__name__)


class ForLoopParser(ScopeParsingStrategy):

    def pre_parse(self, line: str) -> None:
        self.context.setdefault('current_scope_idx', 0)
        if self.pattern == BaseGrammar.FOR_LOOP \
                and not self.context.get('loop_state', {}).get(self.current_scope_idx+1) \
                and self.context.get('loop_state', {}).get(self.current_scope_idx, {}).get('enter_line_idx', -1) + 1 != self.context['source_line_idx']:
            self.current_scope_idx += 1
            # Required to keep track where FOR LOOP enters
            self.context.setdefault('loop_state', {})\
                .setdefault(self.current_scope_idx, {})\
                .setdefault('enter_line_idx', self.context['source_line_idx'] - 1)
        elif self.pattern == BaseGrammar.ENDFOR and self.current_scope_idx not in self.context.get('loop_state', {}):
            self.raise_exception('Syntax error: attempted to close non-existing loop')

    def retrieve_loop_tokens(self, line: str) -> dict:
        """ Retrieves tokens from received loop statement """
        parsed_string = line.split('IN', 1)
        return {
            'variable_name': parsed_string[0].split('FOR', 1)[1].strip(),
            'iterable': iter(get_real_value(self.context, parsed_string[1].strip()) or [])
        }

    def parse(self, line: str) -> None:
        if self.pattern == BaseGrammar.ENDFOR:
            if self.context['loop_state'][self.current_scope_idx].get('iteration_completed'):
                self.context['variable_mapping'].pop(self.context['loop_state'][self.current_scope_idx]['iterator_context']['variable_name'], None)
                self.context['loop_state'].pop(self.current_scope_idx, None)
                self.current_scope_idx -= 1
                self.context['skip_copy'] = True
                return
            else:
                self.context['loop_state'][self.current_scope_idx].setdefault('exit_line_idx', self.context['source_line_idx'] - 1)
                self.context['force_line_idx'] = self.context['loop_state'][self.current_scope_idx]['enter_line_idx'] + 1
        else:
            if not self.context['loop_state'][self.current_scope_idx].get('iterator_context'):
                self.context['loop_state'][self.current_scope_idx]['iterator_context'] = self.retrieve_loop_tokens(line)
            iterator_context = self.context['loop_state'][self.current_scope_idx]['iterator_context']
            try:
                self.context['variable_mapping'][iterator_context['variable_name']] = next(iterator_context['iterable'])
                print(f"Next variable {iterator_context['variable_name']} value "
                      f"- {self.context['variable_mapping'][iterator_context['variable_name']]}")
            except StopIteration:
                logger.info(f'Iteration of condition {line} stopped, exiting loop')
                self.context['loop_state'][self.current_scope_idx]['iteration_completed'] = True
                self.context['skip_copy'] = True
                if 'exit_line_idx' in self.context['loop_state'][self.current_scope_idx]:
                    self.context['force_line_idx'] = self.context['loop_state'][self.current_scope_idx]['exit_line_idx'] + 1
                # else:
                #     self.raise_exception('Missing closing loop statement')
