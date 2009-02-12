#
# Test harness for running Microsoft::Scripting::Silverlight tests. 
#
# TODO should this depend on Microsoft::Scripting::Silverlight at all?

include Microsoft::Scripting::Silverlight
SILVERLIGHT = true

require 'debugger'

#
# 'bacon' is the spec framework used for the tests
#
$: << "lib/bacon/lib"
require 'bacon'

#
# 'mocha' is the mocking framework used for the tests
#
#$: << "lib/mocha/lib"
#require 'mocha_standalone'

#
# TODO better way to redirect output?
#
class IO
  def write(str)
    Repl.current.output_buffer.write(str)
  end
end

#
# Redefine at_exit to simply collect the blocks passed to it
#
$at_exit_blocks = []

module Kernel
  def at_exit(&block)
    $at_exit_blocks.push block
  end
end

Bacon.summary_on_exit

def execute_at_exit_blocks
  while !$at_exit_blocks.empty?
    $at_exit_blocks.pop.call
  end
end

# 
# Test Running
#
# TODO need a way to walk all *_test.rb files in tests directory

$test_files = %W(
  console
  dynamic_application
  extension_types
  package
  window
)

$integration_files = [
  '01',
  'args',
  'auto_addref',
  'error_handle',
  'execfile',
  'issubclass',
  'modules',
  'multi_import',
  'name',
  'net',
  'querystring',
  're',
  'smoke',
  'sys_path',
  's_clock_rb',
  's_dlr_console',
  's_fractulator',
  'thread',
  'utf8',
  'xamlloader',
  'xcode',
  'xcode_semantics',
  'x_attribute_error',
  'x_devidebyzero',
  'x_import_1',
  'x_import_2',
  'x_import_3',
  'x_rethrow',
  'x_syntax_error',
  'x_typeerror'
]

def run_test(test)
  if $test_files.include? test
    load "tests/#{test}_test.rb"
  elsif $integration_files.include? test
    load "integration/test_#{test}.rb"
  else
    raise "#{test} is not a known test (check the $test_files list)"
  end
end

$: << "lib"
#
# test helpers
# 
require 'helper'

#
# run and report results of the tests
#
def run_tests
  $test_files.each { |t| run_test t }
  $integration_files.each { |t| run_test t }
  execute_at_exit_blocks
end

Repl.current.input_buffer.write("run_tests\n")