import os
import argparse
import logging
from lib import settings, phase_1
import tensorflow as tf


def main(**kwargs):
  sett = settings.settings(kwargs["config"])
  stats = settings.stats(os.path.join(sett.path, "stats.yaml"))
  summary_writer = tf.summary.create_file_writer(kwargs["logdir"])
  psnr_model = phase_1.Model(
      data_dir=kwargs["data_dir"],
      summary_writer=summary_writer)
  if not stats["train_step_1"]:
    psnr_model.train()
    stats["train_step_1"] = True


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--config", "config.yaml", "Path to configuration file.")
  parser.add_argument("--data_dir", None, "Directory to put the Data.")
  parser.add_argument("--model_dir", None, "Directory to put the model in.")
  parser.add_argument("--log_dir", None, "Directory to story Summaries.")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  FLAGS, unparsed = parser.parse_known_args()
  levels = [logging.WARNING, logging.INFO, logging.DEBUG]
  level = levels[min(FLAGS.verbose, len(levels) - 1)]
  logging.basicConfig(
      level=level,
      format="%(asctime)s: %(levelname)s: %(message)s")
