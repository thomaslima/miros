import pytest
from miros import signals, Event, return_status
from miros import HsmWithQueues, spy_on
import pprint


def pp(item):
  print("")
  pprint.pprint(item)


################################################################################
#                            HsmQueues Graph G1                                #
################################################################################
# The following state chart is used to test topology G
#
#                   +-------------------------------- g1_s1 --------------+
# +---g1_s0------+  | *i/fifo(e)                                          |
# |+-g1_s01-----+|  |                      +---------g1_s22 ----------+   |
# ||e/fifo(a)   |+------c------------------>  *i/fifo(d)              |   |
# ||e/lifo(f)   ||  |                      |                          |   |
# ||e/recall()  <-e-+                      | +-------g1_s3 ---------+ |   |
# |+------------+|  |                      | | *i/defer(f)          | |   |
# |+------------+|  | +-------g1_s21----+  | |    +----g1_s32-----+ | |   |
# +-+------------+  | | +--g1_s211-----+|  | |    |  +-g1_s321--+ | | |   |
#   |               | | |+-g1_s2111+   ||  | |    |  |          | | | |   |
#   |               | | ||         |   ||  | |    |  |          | | | |   |
#   |               | | ||         |   ||  | |    |  |          | | | |   |
#   |               | | ||         |   ||  | |    |  |          | | | |   |
#   |               | | ||         |   |+-------b---->          <----f----+
#   |               | | ||         |   ||  | |    |  |          | | | |   |
#   |               | | ||         |   ||  | |    |  |          | | | |   |
#   +----------f--------->         |   ||  | |  +---->          | | | |   |
#                   | | ||         |   ||  | |  | |  |          | | | |   |
#                   | | |++--------+   ||  | |  | |  |          | | | +-d->
#                   | | +-|------------+|  | |  | |  +----------+ | | |   |
#                   | +---|-------------+  | |  | +---------------+ | |   |
#                   |     |                | +--|-------------------+ |   |
#                   |     +------------a--------+                     |   |
#                   |                      +--------------------------+   |
#                   |                                                     |
#                   +-----------------------------------------------------+
#
# This is used for testing the type E topology in the trans_ method of the HsmEventProcessor
# class.
#   * test_hsm_next_rtc         - start in hsm_queues_graph_g1_s22
#   * test_hsm_complete_circuit - start in hsm_queues_graph_g1_s22
# '''
@spy_on
def hsm_queues_graph_g1_s0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.F):
    status = chart.trans(hsm_queues_graph_g1_s2111)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def hsm_queues_graph_g1_s01(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.post_fifo(Event(signal=signals.A))
    chart.post_lifo(Event(signal=signals.F))
    chart.recall()
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(hsm_queues_graph_g1_s22)
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s0
  return status


@spy_on
def hsm_queues_graph_g1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    chart.post_fifo(Event(signal=signals.E))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.F):
    status = chart.trans(hsm_queues_graph_g1_s321)
  elif(e.signal == signals.E):
    status = chart.trans(hsm_queues_graph_g1_s01)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def hsm_queues_graph_g1_s21(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(hsm_queues_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s1
  return status


@spy_on
def hsm_queues_graph_g1_s211(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s21
  return status


@spy_on
def hsm_queues_graph_g1_s2111(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(hsm_queues_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s211
  return status


@spy_on
def hsm_queues_graph_g1_s22(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.post_fifo(Event(signal=signals.D))
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = chart.trans(hsm_queues_graph_g1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s1
  return status


@spy_on
def hsm_queues_graph_g1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.defer(Event(signal=signals.F))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s22
  return status


@spy_on
def hsm_queues_graph_g1_s32(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s3
  return status


@spy_on
def hsm_queues_graph_g1_s321(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, hsm_queues_graph_g1_s32
  return status


@pytest.mark.topology_g
@pytest.mark.topology_h
@pytest.mark.rtc
def test_hsm_spy_rtc():
  chart = HsmWithQueues(instrumented=True)
  chart.start_at(hsm_queues_graph_g1_s22)
  assert(chart.spy_rtc() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s1',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
     'INIT_SIGNAL:hsm_queues_graph_g1_s22',
     'POST_FIFO:D',
     '<- Queued:(1) Deferred:(0)'
     ]
  )
  chart.next_rtc()
  assert(chart.spy_rtc() ==
    [
     'D:hsm_queues_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s22',
     'INIT_SIGNAL:hsm_queues_graph_g1_s1',
     'POST_FIFO:E',
     '<- Queued:(1) Deferred:(0)'
    ]
  )
  chart.next_rtc()
  assert(chart.spy_rtc() ==
    ['E:hsm_queues_graph_g1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s0',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s1',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s0',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s01',
     'POST_FIFO:A',
     'POST_LIFO:F',
     'INIT_SIGNAL:hsm_queues_graph_g1_s01',
     '<- Queued:(2) Deferred:(0)'
     ]
  )
  chart.next_rtc()
  assert(chart.spy_rtc() ==
    ['F:hsm_queues_graph_g1_s01',
     'F:hsm_queues_graph_g1_s0',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s0',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s1',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s21',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s211',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s2111',
     'INIT_SIGNAL:hsm_queues_graph_g1_s2111',
     '<- Queued:(1) Deferred:(0)'
     ]
  )
  chart.next_rtc()
  assert(chart.spy_rtc() ==
    ['A:hsm_queues_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s2111',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s211',
     'EXIT_SIGNAL:hsm_queues_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s21',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s3',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s32',
     'ENTRY_SIGNAL:hsm_queues_graph_g1_s321',
     'INIT_SIGNAL:hsm_queues_graph_g1_s321',
     '<- Queued:(0) Deferred:(0)'
     ]
  )
  chart.next_rtc()
  assert(chart.spy_rtc() == ['<- Queued:(0) Deferred:(0)'])


@pytest.mark.topology_g
@pytest.mark.topology_h
@pytest.mark.complete_circuit
def test_hsm_complete_circuit():
  chart = HsmWithQueues(instrumented=True)
  chart.start_at(hsm_queues_graph_g1_s22)
  chart.complete_circuit()
  assert(
      chart.spy_full() ==
      ['START',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s1',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
       'INIT_SIGNAL:hsm_queues_graph_g1_s22',
       'POST_FIFO:D',
       '<- Queued:(1) Deferred:(0)',
       'D:hsm_queues_graph_g1_s22',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s22',
       'INIT_SIGNAL:hsm_queues_graph_g1_s1',
       'POST_FIFO:E',
       '<- Queued:(1) Deferred:(0)',
       'E:hsm_queues_graph_g1_s1',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s01',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s0',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s1',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s0',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s01',
       'POST_FIFO:A',
       'POST_LIFO:F',
       'INIT_SIGNAL:hsm_queues_graph_g1_s01',
       '<- Queued:(2) Deferred:(0)',
       'F:hsm_queues_graph_g1_s01',
       'F:hsm_queues_graph_g1_s0',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s01',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s01',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s2111',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s0',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s211',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s21',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s0',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s1',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s21',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s211',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s2111',
       'INIT_SIGNAL:hsm_queues_graph_g1_s2111',
       '<- Queued:(1) Deferred:(0)',
       'A:hsm_queues_graph_g1_s2111',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s321',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s2111',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s32',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s2111',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s211',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s211',
       'EXIT_SIGNAL:hsm_queues_graph_g1_s21',
       'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s21',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s3',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s32',
       'ENTRY_SIGNAL:hsm_queues_graph_g1_s321',
       'INIT_SIGNAL:hsm_queues_graph_g1_s321',
       '<- Queued:(0) Deferred:(0)']
  )


@pytest.mark.topology_g
@pytest.mark.topology_h
@pytest.mark.defer
@pytest.mark.recall
def test_hsm_trace_output():
  chart = HsmWithQueues(instrumented=True)
  chart.start_at(hsm_queues_graph_g1_s3)
  chart.dispatch(Event(signals.E))
  chart.complete_circuit()
  assert(
      chart.spy_full() ==
        ['START',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s1',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s3',
         'INIT_SIGNAL:hsm_queues_graph_g1_s3',
         'POST_DEFERRED:F',
         '<- Queued:(0) Deferred:(1)',
         'E:hsm_queues_graph_g1_s3',
         'E:hsm_queues_graph_g1_s22',
         'E:hsm_queues_graph_g1_s1',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s3',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s22',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s01',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s0',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s1',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s0',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s01',
         'POST_FIFO:A',
         'POST_LIFO:F',
         'RECALL:F',
         'POST_FIFO:F',
         'INIT_SIGNAL:hsm_queues_graph_g1_s01',
         'F:hsm_queues_graph_g1_s01',
         'F:hsm_queues_graph_g1_s0',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s01',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s01',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s2111',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s0',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s211',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s21',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s0',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s1',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s21',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s211',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s2111',
         'INIT_SIGNAL:hsm_queues_graph_g1_s2111',
         '<- Queued:(2) Deferred:(0)',
         'A:hsm_queues_graph_g1_s2111',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s321',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s2111',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s32',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s2111',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s211',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s211',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s21',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s21',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s3',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s32',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s321',
         'INIT_SIGNAL:hsm_queues_graph_g1_s321',
         '<- Queued:(1) Deferred:(0)',
         'F:hsm_queues_graph_g1_s321',
         'F:hsm_queues_graph_g1_s32',
         'F:hsm_queues_graph_g1_s3',
         'F:hsm_queues_graph_g1_s22',
         'F:hsm_queues_graph_g1_s1',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s321',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s321',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s32',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s32',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s3',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
         'EXIT_SIGNAL:hsm_queues_graph_g1_s22',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s321',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s1',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s32',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s3',
         'SEARCH_FOR_SUPER_SIGNAL:hsm_queues_graph_g1_s22',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s22',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s3',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s32',
         'ENTRY_SIGNAL:hsm_queues_graph_g1_s321',
         'INIT_SIGNAL:hsm_queues_graph_g1_s321',
         '<- Queued:(0) Deferred:(0)']
      )


