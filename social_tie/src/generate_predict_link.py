class GeneratePredictedLink(object):
    """docstring for GeneratePredictedLink"""

    def __init__(self):
        super(GeneratePredictedLink, self).__init__()
        self.train_mark = list()
        self.test_mark = list()
        self.pred = list()
        self.train = list()
        self.test = list()

    def load_mark_file(self, train_mark_name, test_mark_name):
        in_train_mark = open(train_mark_name, 'r')
        in_test_mark = open(test_mark_name, 'r')
        for line in in_train_mark:
            content = line.replace("(", "").replace(")", "").replace("'", "").replace(",", "").replace("\n", "")
            content = content.split(" ")
            self.train_mark.append(content)
        for line in in_test_mark:
            content = line.replace("(", "").replace(")", "").replace("'", "").replace(",", "").replace("\n", "")
            content = content.split(" ")
            self.test_mark.append(content)
        in_train_mark.close()
        in_test_mark.close()

    def load_pred(self, pred_name):
        in_pred = open(pred_name, 'r')
        for line in in_pred:
            self.pred.append(line.replace("\n", ""))

    def load_factor_file(self, train_name, test_name):
        in_train = open(train_name, 'r')
        in_test = open(test_name, 'r')
        for line in in_train:
            content = line.split(" ")
            if content[0][0] == "?":
                continue
            elif content[0][0] == "+":
                self.train.append(content[0][1:])
        for line in in_test:
            content = line.split(" ")
            self.test.append(content[0][1:])

    def generate(self, outputname, label_outname, unlabel_outname):
        train_final = self.pred + self.train
        unlabel_num = len(self.pred)
        assert(len(self.train_mark) == len(train_final))
        assert(len(self.test_mark) == len(self.test))
        outfile = open(outputname, 'w')
        label_outfile = open(label_outname, 'w')
        unlabel_outfile = open(unlabel_outname, 'w')
        for i in range(len(self.train_mark)):
            if i < unlabel_num:
                outfile.write("unlabel " + self.train_mark[i][0] + " " + self.train_mark[i][1] + " " + train_final[i] + "\n")
                unlabel_outfile.write("unlabel " + self.train_mark[i][0] + " " + self.train_mark[i][1] + " " + train_final[i] + "\n")
            else:
                outfile.write("label " + self.train_mark[i][0] + " " + self.train_mark[i][1] + " " + train_final[i] + "\n")
                label_outfile.write("label " + self.train_mark[i][0] + " " + self.train_mark[i][1] + " " + train_final[i] + "\n")
        for i in range(len(self.test_mark)):
            outfile.write("label " + self.test_mark[i][0] + " " + self.test_mark[i][1] + " " + self.test[i] + "\n")
            label_outfile.write("label " + self.test_mark[i][0] + " " + self.test_mark[i][1] + " " + self.test[i] + "\n")
        outfile.close()
        label_outfile.close()
        unlabel_outfile.close()


def main():
    gpl = GeneratePredictedLink()
    gpl.load_mark_file("../results/train.mark", "../results/test.mark")
    gpl.load_pred("../results/pred.txt")
    gpl.load_factor_file("../results/train.txt", "../results/test.txt")
    gpl.generate("../results/results.txt", "../results/results_label.txt", "../results/results_unlabel.txt")


if __name__ == '__main__':
    main()
