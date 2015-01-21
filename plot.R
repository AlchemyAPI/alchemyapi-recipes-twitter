library('ggplot2')

#-----------------------------------------------------------
#
#   Sentiment scores histogram and Kernel density plot
#
#-----------------------------------------------------------

pos_data <- read.table("scores.pos", header=FALSE)
neg_data <- read.table("scores.neg", header=FALSE)

p <- pos_data[,1]
n <- neg_data[,1]

score_data <- data.frame(scores = c(p, n), labels=c(rep.int("p", length(p)), rep.int("n", length(n))))

# Plot the raw data
sentiment_hist <- ggplot(score_data, aes(x=scores,fill=labels), xlab="Test") 
sentiment_hist <- sentiment_hist + geom_histogram(data=subset(score_data, labels=="p")) 
sentiment_hist <- sentiment_hist + geom_histogram(data=subset(score_data, labels=="n"));
sentiment_hist <- sentiment_hist + xlab("Sentiment score") + ylab("Number of Tweets");
sentiment_hist <- sentiment_hist + ggtitle("Twitter Sentiment");
sentiment_hist + scale_fill_manual(name = "", values = c("red", "blue"), labels = c("Negative", "Positive"))
ggsave(filename="twitter_sentiment_raw.png")

# Make the same plot, converting to kernel densities
sentiment_dens <- ggplot(score_data, aes(x=scores,fill=labels))
sentiment_dens <- sentiment_dens + geom_density(data=subset(score_data, labels=="p"))
sentiment_dens <- sentiment_dens + geom_density(data=subset(score_data, labels=="n"));
sentiment_dens <- sentiment_dens + xlab("Sentiment score") + ylab("Kernel density");
sentiment_dens <- sentiment_dens + ggtitle("Twitter Sentiment");
sentiment_dens + scale_fill_manual(name = "", values = c("red", "blue"), labels = c("Negative", "Positive"))
ggsave(filename="twitter_sentiment_kernel.png")


#--------------------------------------------------------------------------
#
#   Bar chart showing when Twitter volume as a function of hour in the day
#
#--------------------------------------------------------------------------

pos_time_file = file("times.pos", open="r")
neg_time_file = file("times.neg", open="r")
pos_times <- as.POSIXlt(readLines(pos_time_file))
neg_times <- as.POSIXlt(readLines(neg_time_file))

pos_hours <- round(pos_times, "hours")
neg_hours <- round(neg_times, "hours")

pos_data <- data.frame(formatted = pos_hours)
pos_data$hours <- substr(pos_data$formatted, 12, 16)
neg_data <- data.frame(formatted = neg_hours)
neg_data$hours <- substr(neg_data$formatted, 12, 16)

count_data <- data.frame(times = c(pos_data$hours, neg_data$hours), labels=c(rep.int("p", length(pos_data$hours)), rep.int("n", length(neg_data$hours))))

time_chart <- ggplot(count_data, aes(x=times, fill=labels)) + geom_bar()
time_chart <- time_chart + xlab("Times (MDT)") + ylab("Number of Tweets");
time_chart <- time_chart + ggtitle("Twitter Volume");
time_chart <- time_chart + scale_fill_manual(name = "", values = c("red", "blue"), labels = c("Negative", "Positive"))
time_chart + theme(axis.text.x = element_text(angle=45, hjust=1))
ggsave(filename="twitter_sentiment_volume.png")
