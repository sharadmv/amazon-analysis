import os
import logging
logging.basicConfig()

logger = logging.getLogger('lda')
logger.setLevel(logging.DEBUG)

from path import path

from rosetta.text.vw_helpers import LDAResults
from rosetta.text.text_processors import SFileFilter, VWFormatter, TokenizerBasic
from rosetta.text.streamers import TextIterStreamer

class LDA:
    def __init__(self, input_file,
                 num_topics=10, alpha=0.1, rho=0.1, output_dir=path('temp'),
                 cache_file='temp.cache', num_passes=10, bit_precision=16,
                 D=10000):
        self.input_file = input_file
        self.num_topics = num_topics
        self.alpha = alpha
        self.rho = rho
        self.output_dir = output_dir
        self.cache_file = output_dir / cache_file
        self.num_passes = num_passes
        self.bit_precision = bit_precision
        self.D = D

        self.reviews_file = output_dir / "reviews.txt"
        self.filtered_file = output_dir / "filtered.vw"
        self.out_file = output_dir / "docs.vw"

    def convert(self, force=False):
        logger.info("Creating reviews file...")
        if force or not self.reviews_file.exists():
            with open(self.reviews_file, 'w') as fp:
                for line in self.input_file:
                    row = line.strip().split(' ', 5)
                    if len(row) > 5:
                        user_id, item_id, rating, timestamp, word_count, review = row
                        print >>fp, review
        logger.info("Creating filtered dat file...")
        def file_gen():
            with open(self.reviews_file, 'r') as fp:
                for index, line in enumerate(fp):
                    yield {
                        'text': line.strip(),
                        'doc_id': str(index),
                    }

        if force or not self.filtered_file.exists():
            with open(self.filtered_file, 'w') as fp:
                tokenizer = TokenizerBasic()
                stream = TextIterStreamer(file_gen(), tokenizer=tokenizer)
                stream.to_vw(fp, n_jobs=1)

        if force or not self.out_file.exists():
            sff = SFileFilter(VWFormatter())
            sff.load_sfile(self.filtered_file)

            df = sff.to_frame()
            df.head()
            df.describe()

            print "Filtering dat file..."
            sff.filter_extremes(doc_freq_min=50, doc_fraction_max=0.8)
            print "Sparsifying..."
            sff.compactify()
            sff.save(self.output_dir / 'sff_file.pkl')
            print "Outputting final file..."
            sff.filter_sfile(self.filtered_file, self.out_file)



    def run(self, force=False):
        if not self.output_dir.exists():
            self.output_dir.mkdir()

        self.convert(force)


        if (self.output_dir / self.cache_file).exists():
            self.cache_file.remove()

        cmd = "vw --lda {num_topics} --cache_file {cache_file} --passes {num_passes}"\
                " -p {output_dir}/prediction.dat --readable_model {output_dir}/topics.dat -b {bit_precision} {out_file}"
        filled_cmd = cmd.format(
            num_topics=self.num_topics,
            num_passes=self.num_passes,
            cache_file=self.cache_file,
            output_dir=self.output_dir,
            bit_precision=self.bit_precision,
            out_file=self.out_file
        )
        print filled_cmd
        os.system(filled_cmd)
        lda = LDAResults(self.output_dir / 'topics.dat',
                         self.output_dir / 'prediction.dat',
                         self.output_dir / 'sff_file.pkl',
                        num_topics=self.num_topics)
        lda.print_topics()
