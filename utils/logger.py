import time
log_fd = open(time.strftime("%Y-%m-%d") +
              '.log', mode='a+', encoding='utf8')


def print_log(log):
    print('{} {}'.format(time.strftime("%Y-%m-%d-%H-%M-%S"), log))
    print('{} {}'.format(time.strftime("%Y-%m-%d-%H-%M-%S"), log), file=log_fd)
    log_fd.flush()