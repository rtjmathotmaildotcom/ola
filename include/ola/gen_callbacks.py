#!/usr/bin/python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# gen_callbacks.py
# Copyright (C) 2010 Simon Newton


import textwrap


def Header():
  print textwrap.dedent("""\
  /*
   *  This program is free software; you can redistribute it and/or modify
   *  it under the terms of the GNU General Public License as published by
   *  the Free Software Foundation; either version 2 of the License, or
   *  (at your option) any later version.
   *
   *  This program is distributed in the hope that it will be useful,
   *  but WITHOUT ANY WARRANTY; without even the implied warranty of
   *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   *  GNU Library General Public License for more details.
   *
   *  You should have received a copy of the GNU General Public License
   *  along with this program; if not, write to the Free Software
   *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
   *
   * Callback.h
   * Callback classes, these are similar to closures but can take arguments at
   * exec time.
   * Copyright (C) 2005-2010 Simon Newton
   *
   * THIS FILE IS AUTOGENERATED!
   * Please run edit & run gen_callbacks.py if you need to add more types.
   */

  #ifndef INCLUDE_OLA_CALLBACK_H_
  #define INCLUDE_OLA_CALLBACK_H_

  namespace ola {
  """)

def Footer():
  print textwrap.dedent("""\
  }  // ola
  #endif  // INCLUDE_OLA_CALLBACK_H_""")

def GenerateBase(number_of_args):
  """Generate the base Callback classes."""
  optional_comma = ''

  if number_of_args > 0:
    optional_comma = ', '

  typenames = ', '.join('typename Arg%d' % i for i in xrange(number_of_args))
  arg_list = ', '.join('Arg%d arg%d' % (i, i) for i in xrange(number_of_args))
  args = ', '.join('arg%d' % i for i in xrange(number_of_args))

  arg_types = ', '.join('Arg%d' % i for i in xrange(number_of_args))

  # generate the base callback class
  print '// %d argument callbacks' % number_of_args
  print 'template <typename ReturnType%s%s>' % (optional_comma, typenames)
  print 'class BaseCallback%d {' % number_of_args
  print '  public:'
  print '    virtual ~BaseCallback%d() {}' % number_of_args
  print '    virtual ReturnType Run(%s) = 0;' % arg_list
  print '    virtual ReturnType DoRun(%s) = 0;' % arg_list
  print '};'
  print ''
  print ''

  # generate the multi-use version of the callback
  print '// A callback, this can be called multiple times'
  print 'template <typename ReturnType%s%s>' % (optional_comma, typenames)
  print ('class Callback%d: public BaseCallback%d<ReturnType%s%s> {' %
         (number_of_args, number_of_args, optional_comma, arg_types))
  print '  public:'
  print '    virtual ~Callback%d() {}' % number_of_args
  print ('    ReturnType Run(%s) { return this->DoRun(%s); }' %
         (arg_list, args))
  print '};'
  print ''
  print ''

  # generate the single-use version of the callback
  print "// A single use callback, this deletes itself after it's run."
  print 'template <typename ReturnType%s%s>' % (optional_comma, typenames)
  print ('class SingleUseCallback%d: public BaseCallback%d<ReturnType%s%s> {' %
         (number_of_args, number_of_args, optional_comma, arg_types))
  print '  public:'
  print '    virtual ~SingleUseCallback%d() {}' % number_of_args
  print '    ReturnType Run(%s) {' % arg_list
  print '      ReturnType ret = this->DoRun(%s);' % args
  print '      delete this;'
  print '      return ret;'
  print '    }'
  print '};'
  print ''
  print ''

  # the void specialization
  print "// A single use callback returning void."
  print 'template <%s>' % typenames
  print ('class SingleUseCallback%d<void%s%s>: public BaseCallback%d<void%s%s> {' %
         (number_of_args, optional_comma, arg_types, number_of_args,
           optional_comma, arg_types))
  print '  public:'
  print '    virtual ~SingleUseCallback%d() {}' % number_of_args
  print '    void Run(%s) {' % arg_list
  print '      this->DoRun(%s);' % args
  print '      delete this;'
  print '    }'
  print '};'
  print ''
  print ''


def GenerateHelperFunction(bind_count,
                           exec_count,
                           function_name,
                           parent_class,
                           is_method=True):
  """Generate the helper functions which create callbacks.

  Args:
    bind_count the number of args supplied at create time.
    exec_count the number of args supplied at exec time.
    function_name what to call the helper function
    parent_class the parent class to use
    is_method True if this is a method callback, False if this is a function
      callback.
    """
  optional_comma = ''
  if bind_count > 0 or exec_count > 0:
    optional_comma = ', '

  typenames = (['typename A%d' % i for i in xrange(bind_count)] +
               ['typename Arg%d' % i for i in xrange(exec_count)])
  bind_types = ['A%d' % i for i in xrange(bind_count)]
  exec_types = ['Arg%d' % i for i in xrange(exec_count)]
  method_types = ', '.join(bind_types + exec_types)
  if exec_count > 0:
    exec_types = [''] + exec_types
  exec_type_str = ', '.join(exec_types)
  optional_class, ptr_name, signature = '', 'callback', '*callback'
  if is_method:
    optional_class, ptr_name, signature = (
        'typename Class, ', 'method', 'Class::*method')

  # The single use helper function
  print '// Helper method to create a new %s.' % parent_class
  print ('template <%stypename ReturnType%s%s>' %
         (optional_class, optional_comma, ', '.join(typenames)))
  print ('inline %s%d<ReturnType%s>* %s(' %
         (parent_class, exec_count, exec_type_str, function_name))
  if is_method:
    print '    Class* object,'
  if bind_count:
    print '    ReturnType (%s)(%s),' % (signature, method_types)
    for i in xrange(bind_count):
      suffix = ','
      if i == bind_count - 1:
        suffix = ') {'
      print '    A%d a%d%s' % (i, i, suffix)
  else:
    print '    ReturnType (%s)(%s)) {' % (signature, method_types)

  if is_method:
    print '  return new MethodCallback%d_%d<Class,' % (bind_count, exec_count)
  else:
    print '  return new FunctionCallback%d_%d<' % (bind_count, exec_count)
  print ('                               %s%d<ReturnType%s>,'
         % (parent_class, exec_count, exec_type_str))
  if bind_count > 0 or exec_count > 0:
    print '                               ReturnType,'
  else:
    print '                               ReturnType>('
  for i in xrange(bind_count):
    if i == bind_count - 1 and exec_count == 0:
      suffix = '>('
    else:
      suffix = ','
    print '                               A%d%s' % (i, suffix)
  for i in xrange(exec_count):
    suffix = ','
    if i == exec_count - 1:
      suffix = '>('
    print '                               Arg%d%s' % (i, suffix)
  if is_method:
    print '      object,'
  if bind_count:
    print '      %s,' % ptr_name
  else:
    print '      %s);' % ptr_name
  for i in xrange(bind_count):
    suffix = ','
    if i == bind_count - 1:
      suffix = ');'
    print '      a%d%s' % (i, suffix)
  print '}'
  print ''
  print ''


def GenerateMethodCallback(bind_count,
                           exec_count,
                           is_method=True):
  """Generate the specific function callback & helper methods.
    bind_count the number of args supplied at create time.
    exec_count the number of args supplied at exec time.
    is_method True if this is a method callback, False if this is a function
      callback.
  """
  optional_comma = ''
  if bind_count > 0 or exec_count > 0:
    optional_comma = ', '

  typenames = (['typename A%d' % i for i in xrange(bind_count)] +
               ['typename Arg%d' % i for i in xrange(exec_count)])

  bind_types = ['A%d' % i for i in xrange(bind_count)]
  exec_types = ['Arg%d' % i for i in xrange(exec_count)]

  method_types = ', '.join(bind_types + exec_types)
  method_args = (['m_a%d' % i for i in xrange(bind_count)] +
                  ['arg%d' % i for i in xrange(exec_count)])

  exec_args = ', '.join(['Arg%d arg%d' % (i, i) for i in xrange(exec_count)])
  bind_args = ', '.join(['A%d a%d' % (i, i) for i in xrange(bind_count)])

  optional_class, method_or_function, class_name = (
      '', 'Function', 'FunctionCallback')
  class_param, signature = '', '*callback';
  if is_method:
    optional_class, method_or_function, class_name = (
        'typename Class, ', 'Method', 'MethodCallback')
    class_param, signature = 'Class *object, ', 'Class::*Method'

  print ('// A %s callback with %d create-time args and %d exec time '
         'args' % (method_or_function, bind_count, exec_count))
  print ('template <%stypename Parent, typename ReturnType%s%s>' %
         (optional_class, optional_comma, ', '.join(typenames)))

  print 'class %s%d_%d: public Parent {' % (class_name, bind_count, exec_count)
  print '  public:'
  if is_method:
    print '    typedef ReturnType (%s)(%s);' % (signature, method_types)
  else:
    print '    typedef ReturnType (*Function)(%s);' % (method_types)

  if bind_count:
    print ('    %s%d_%d(%s%s callback, %s):' %
           (class_name, bind_count, exec_count, class_param,
            method_or_function, bind_args))
  else:
    print ('    %s%d_%d(%s%s callback):' %
           (class_name, bind_count, exec_count, class_param,
            method_or_function))
  print '      Parent(),'
  if is_method:
    print '      m_object(object),'
  if bind_count:
    print '      m_callback(callback),'
    for i in xrange(bind_count):
      suffix = ','
      if i == bind_count - 1:
        suffix = ' {}'
      print '      m_a%d(a%d)%s' % (i, i, suffix)
  else:
    print '      m_callback(callback) {}'
  print '    ReturnType DoRun(%s) {' % exec_args
  if is_method:
    print '      return (m_object->*m_callback)(%s);' % ', '.join(method_args)
  else:
    print '      return m_callback(%s);' % ', '.join(method_args)
  print '    }'

  print '  private:'
  if is_method:
    print '    Class *m_object;'
  print '    %s m_callback;' % method_or_function
  for i in xrange(bind_count):
    print '  A%d m_a%d;' % (i, i)
  print '};'
  print ''
  print ''

  # generate the helper methods
  GenerateHelperFunction(bind_count,
                         exec_count,
                         'NewSingleCallback',
                         'SingleUseCallback',
                         is_method)
  GenerateHelperFunction(bind_count,
                         exec_count,
                         'NewCallback',
                         'Callback',
                         is_method)


def main():
  Header()

  # exec_time : [bind time args]
  calback_types = {0: [0, 1, 2, 3, 4],
                   1: [0, 1, 2, 3, 4],
                   2: [0, 1, 2, 3, 4],
                   3: [0, 1, 2, 3, 4],
                   4: [0, 1, 2, 3, 4],
                  }

  for exec_time in sorted(calback_types):
    GenerateBase(exec_time)
    for bind_time in calback_types[exec_time]:
      GenerateMethodCallback(bind_time, exec_time, is_method=False);
      GenerateMethodCallback(bind_time, exec_time)
  Footer()


main()
