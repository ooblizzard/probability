# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Dependency imports
import numpy as np
from scipy import stats
import tensorflow as tf
import tensorflow_probability as tfp

from tensorflow.python.framework import test_util

tfd = tfp.distributions


class ParetoTest(tf.test.TestCase):

  def _scipy_pareto(self, concentration, scale):
    # In scipy pareto is defined with scale = 1, so we need to scale.
    return stats.pareto(concentration, scale=scale)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoShape(self):
    scale = tf.constant([2.] * 5)
    concentration = tf.constant([2.] * 5)
    pareto = tfd.Pareto(concentration, scale)

    self.assertEqual(self.evaluate(pareto.batch_shape_tensor()), (5,))
    self.assertEqual(pareto.batch_shape, tf.TensorShape([5]))
    self.assertAllEqual(self.evaluate(pareto.event_shape_tensor()), [])
    self.assertEqual(pareto.event_shape, tf.TensorShape([]))

  @test_util.run_in_graph_and_eager_modes()
  def testParetoShapeBroadcast(self):
    scale = tf.constant([[3., 2.]])
    concentration = tf.constant([[4.], [5.], [6.]])
    pareto = tfd.Pareto(concentration, scale)

    self.assertAllEqual(self.evaluate(pareto.batch_shape_tensor()), (3, 2))
    self.assertAllEqual(pareto.batch_shape, tf.TensorShape([3, 2]))
    self.assertAllEqual(self.evaluate(pareto.event_shape_tensor()), [])
    self.assertEqual(pareto.event_shape, tf.TensorShape([]))

  @test_util.run_in_graph_and_eager_modes()
  def testInvalidScale(self):
    invalid_scales = [-.01, 0., -2.]
    concentration = 3.
    for scale in invalid_scales:
      with self.assertRaisesOpError("Condition x > 0"):
        pareto = tfd.Pareto(concentration, scale, validate_args=True)
        self.evaluate(pareto.scale)

  @test_util.run_in_graph_and_eager_modes()
  def testInvalidConcentration(self):
    scale = 1.
    invalid_concentrations = [-.01, 0., -2.]
    for concentration in invalid_concentrations:
      with self.assertRaisesOpError("Condition x > 0"):
        pareto = tfd.Pareto(concentration, scale, validate_args=True)
        self.evaluate(pareto.concentration)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoLogPdf(self):
    batch_size = 6
    scale = tf.constant([3.] * batch_size)
    scale_v = 3.
    concentration = tf.constant([2.])
    concentration_v = 2.
    x = [3., 3.1, 4., 5., 6., 7.]
    pareto = tfd.Pareto(concentration, scale)
    log_prob = pareto.log_prob(x)
    self.assertEqual(log_prob.shape, (6,))
    self.assertAllClose(
        self.evaluate(log_prob),
        self._scipy_pareto(concentration_v, scale_v).logpdf(x))

    pdf = pareto.prob(x)
    self.assertEqual(pdf.shape, (6,))
    self.assertAllClose(
        self.evaluate(pdf),
        self._scipy_pareto(concentration_v, scale_v).pdf(x))

  def testParetoLogPdfValidateArgs(self):
    batch_size = 3
    scale = tf.constant([2., 3., 4.])
    concentration = tf.constant([2.] * batch_size)
    x = tf.placeholder(tf.float32, shape=[3])
    pareto = tfd.Pareto(concentration, scale, validate_args=True)

    with self.test_session():
      with self.assertRaisesOpError("not in the support"):
        log_prob = pareto.log_prob(x)
        log_prob.eval(feed_dict={x: [2., 3., 3.]})

      with self.assertRaisesOpError("not in the support"):
        log_prob = pareto.log_prob(x)
        log_prob.eval(feed_dict={x: [2., 2., 4.]})

      with self.assertRaisesOpError("not in the support"):
        log_prob = pareto.log_prob(x)
        log_prob.eval(feed_dict={x: [1., 3., 4.]})

  @test_util.run_in_graph_and_eager_modes()
  def testParetoLogPdfMultidimensional(self):
    batch_size = 6
    scale = tf.constant([[2., 4., 5.]] * batch_size)
    scale_v = [2., 4., 5.]
    concentration = tf.constant([[1.]] * batch_size)
    concentration_v = 1.

    x = np.array([[6., 7., 9.2, 5., 6., 7.]], dtype=np.float32).T

    pareto = tfd.Pareto(concentration, scale)
    log_prob = pareto.log_prob(x)
    self.assertEqual(log_prob.shape, (6, 3))
    self.assertAllClose(
        self.evaluate(log_prob),
        self._scipy_pareto(concentration_v, scale_v).logpdf(x))

    prob = pareto.prob(x)
    self.assertEqual(prob.shape, (6, 3))
    self.assertAllClose(
        self.evaluate(prob),
        self._scipy_pareto(concentration_v, scale_v).pdf(x))

  @test_util.run_in_graph_and_eager_modes()
  def testParetoLogCdf(self):
    batch_size = 6
    scale = tf.constant([3.] * batch_size)
    scale_v = 3.
    concentration = tf.constant([2.])
    concentration_v = 2.
    x = [3., 3.1, 4., 5., 6., 7.]
    pareto = tfd.Pareto(concentration, scale)
    log_cdf = pareto.log_cdf(x)
    self.assertEqual(log_cdf.shape, (6,))
    self.assertAllClose(
        self.evaluate(log_cdf),
        self._scipy_pareto(concentration_v, scale_v).logcdf(x))

    cdf = pareto.cdf(x)
    self.assertEqual(cdf.shape, (6,))
    self.assertAllClose(
        self.evaluate(cdf),
        self._scipy_pareto(concentration_v, scale_v).cdf(x))

  @test_util.run_in_graph_and_eager_modes()
  def testParetoLogCdfMultidimensional(self):
    batch_size = 6
    scale = tf.constant([[2., 4., 5.]] * batch_size)
    scale_v = [2., 4., 5.]
    concentration = tf.constant([[1.]] * batch_size)
    concentration_v = 1.

    x = np.array([[6., 7., 9.2, 5., 6., 7.]], dtype=np.float32).T

    pareto = tfd.Pareto(concentration, scale)
    log_cdf = pareto.log_cdf(x)
    self.assertEqual(log_cdf.shape, (6, 3))
    self.assertAllClose(
        self.evaluate(log_cdf),
        self._scipy_pareto(concentration_v, scale_v).logcdf(x))

    cdf = pareto.cdf(x)
    self.assertEqual(cdf.shape, (6, 3))
    self.assertAllClose(
        self.evaluate(cdf),
        self._scipy_pareto(concentration_v, scale_v).cdf(x))

  def testParetoPDFGradientZeroOutsideSupport(self):
    scale = tf.constant(1.)
    concentration = tf.constant(3.)
    # Check the gradient on the undefined portion.
    x = scale - 1

    pareto = tfd.Pareto(concentration, scale)
    pdf = pareto.prob(x)
    self.assertAlmostEqual(self.evaluate(tf.gradients(pdf, x)[0]), 0.)

  def testParetoCDFGradientZeroOutsideSupport(self):
    scale = tf.constant(1.)
    concentration = tf.constant(3.)
    # Check the gradient on the undefined portion.
    x = scale - 1

    pareto = tfd.Pareto(concentration, scale)
    cdf = pareto.cdf(x)
    self.assertAlmostEqual(self.evaluate(tf.gradients(cdf, x)[0]), 0.)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoMean(self):
    scale = [1.4, 2., 2.5]
    concentration = [2., 3., 2.5]
    pareto = tfd.Pareto(concentration, scale)
    self.assertEqual(pareto.mean().shape, (3,))
    self.assertAllClose(
        self.evaluate(pareto.mean()),
        self._scipy_pareto(concentration, scale).mean())

  @test_util.run_in_graph_and_eager_modes()
  def testParetoMeanInf(self):
    scale = [1.4, 2., 2.5]
    concentration = [0.4, 0.9, 0.99]
    pareto = tfd.Pareto(concentration, scale)
    self.assertEqual(pareto.mean().shape, (3,))

    self.assertTrue(
        np.all(np.isinf(self.evaluate(pareto.mean()))))

  @test_util.run_in_graph_and_eager_modes()
  def testParetoVariance(self):
    scale = [1.4, 2., 2.5]
    concentration = [2., 3., 2.5]
    pareto = tfd.Pareto(concentration, scale)
    self.assertEqual(pareto.variance().shape, (3,))
    self.assertAllClose(
        self.evaluate(pareto.variance()),
        self._scipy_pareto(concentration, scale).var())

  @test_util.run_in_graph_and_eager_modes()
  def testParetoVarianceInf(self):
    scale = [1.4, 2., 2.5]
    concentration = [0.4, 0.9, 0.99]
    pareto = tfd.Pareto(concentration, scale)
    self.assertEqual(pareto.variance().shape, (3,))
    self.assertTrue(
        np.all(np.isinf(self.evaluate(pareto.variance()))))

  @test_util.run_in_graph_and_eager_modes()
  def testParetoStd(self):
    scale = [1.4, 2., 2.5]
    concentration = [2., 3., 2.5]
    pareto = tfd.Pareto(concentration, scale)
    self.assertEqual(pareto.stddev().shape, (3,))
    self.assertAllClose(
        self.evaluate(pareto.stddev()),
        self._scipy_pareto(concentration, scale).std())

  @test_util.run_in_graph_and_eager_modes()
  def testParetoMode(self):
    with self.test_session():
      scale = [0.4, 1.4, 2., 2.5]
      concentration = [1., 2., 3., 2.5]
      pareto = tfd.Pareto(concentration, scale)
      self.assertEqual(pareto.mode().shape, (4,))
      self.assertAllClose(
          self.evaluate(pareto.mode()), scale)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoSampleMean(self):
    scale = 4.
    concentration = 3.
    n = int(100e3)
    pareto = tfd.Pareto(concentration, scale)
    samples = pareto.sample(n, seed=123456)
    sample_values = self.evaluate(samples)
    self.assertEqual(samples.shape, (n,))
    self.assertEqual(sample_values.shape, (n,))
    self.assertAllClose(
        sample_values.mean(),
        self._scipy_pareto(concentration, scale).mean(),
        rtol=.01,
        atol=0)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoSampleVariance(self):
    scale = 1.
    concentration = 3.
    n = int(400e3)
    pareto = tfd.Pareto(concentration, scale)
    samples = pareto.sample(n, seed=123456)
    sample_values = self.evaluate(samples)
    self.assertEqual(samples.shape, (n,))
    self.assertEqual(sample_values.shape, (n,))
    self.assertAllClose(
        sample_values.var(),
        self._scipy_pareto(concentration, scale).var(),
        rtol=.03,
        atol=0)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoSampleMultidimensionalMean(self):
    scale = np.array([np.arange(1, 21, dtype=np.float32)])
    concentration = 3.
    pareto = tfd.Pareto(concentration, scale)
    n = int(100e3)
    samples = pareto.sample(n, seed=123456)
    sample_values = self.evaluate(samples)
    self.assertEqual(samples.shape, (n, 1, 20))
    self.assertEqual(sample_values.shape, (n, 1, 20))
    self.assertAllClose(
        sample_values.mean(axis=0),
        self._scipy_pareto(concentration, scale).mean(),
        rtol=.01,
        atol=0)

  @test_util.run_in_graph_and_eager_modes()
  def testParetoSampleMultidimensionalVariance(self):
    scale = np.array([np.arange(1, 11, dtype=np.float32)])
    concentration = 4.
    pareto = tfd.Pareto(concentration, scale)
    n = int(800e3)
    samples = pareto.sample(n, seed=123456)
    sample_values = self.evaluate(samples)
    self.assertEqual(samples.shape, (n, 1, 10))
    self.assertEqual(sample_values.shape, (n, 1, 10))

    self.assertAllClose(
        sample_values.var(axis=0),
        self._scipy_pareto(concentration, scale).var(),
        rtol=.05,
        atol=0)


if __name__ == "__main__":
  tf.test.main()
