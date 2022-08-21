from mothur_py import Mothur
# TODO check if files are in the folder
m = Mothur(mothur_path='/home/rippberger/mothur-1.46.1/mothur', verbosity=2)
m.set.logfile(name="myCollectLogfile", append="T")
m.make.file(inputdir=".", type="fastq", prefix="stability")
m.make.contigs(file="stability.files", processors=56)
m.screen.seqs(fasta="stability.trim.contigs.fasta", contigsreport="stability.contigs.report", group="stability.contigs.groups", maxambig=0, maxhomop=6, minlength=200, maxlength=1000, mismatches=0, processors=56)
m.trim.seqs(fasta="stability.trim.contigs.good.fasta", processors=56, qaverage=25)
m.summary.seqs(fasta="stability.trim.contigs.good.trim.fasta")
m.unique.seqs(fasta="stability.trim.contigs.good.trim.fasta")
m.count.seqs(name="stability.trim.contigs.good.trim.names", group="stability.contigs.good.groups")
m.summary.seqs(fasta="stability.trim.contigs.good.trim.unique.fasta", count="stability.trim.contigs.good.trim.count_table")
m.classify.seqs(fasta="stability.trim.contigs.good.trim.unique.fasta",
                count="stability.trim.contigs.good.trim.count_table",
                template="trainset6_032010.fa",
                taxonomy="trainset6_032010.tax",
                output="simple",
                processors=56)
m.classify.seqs(fasta="stability.trim.contigs.good.trim.unique.fasta",
                count="stability.trim.contigs.good.trim.count_table",
                template="trainset18_062020.rdp.fasta",
                taxonomy="trainset18_062020.rdp.tax",
                output="simple",
                processors=56)

m.rename.file(input="stability.trim.contigs.good.trim.unique.trainset6_032010.wang.tax.summary", new="final.summary")
m.rename.file(input="stability.trim.contigs.good.trim.unique.rdp.wang.tax.summary", new="final.rdp18.summary")

