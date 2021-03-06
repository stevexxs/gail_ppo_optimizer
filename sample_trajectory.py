import argparse
import gym
import os
import numpy as np
from network_models.policy_net import Policy_net
import tensorflow as tf


# noinspection PyTypeChecker
def open_file_and_save(file_path, data):
    """
    :param file_path: type==string
    :param data:
    """
    try:
        with open(file_path, 'ab') as f_handle:
            np.savetxt(f_handle, data, fmt='%s')
    except FileNotFoundError:
        with open(file_path, 'wb') as f_handle:
            np.savetxt(f_handle, data, fmt='%s')


def argparser():
    parser = argparse.ArgumentParser()
    # CartPole-v1, Arcobot-v1, Pendulum-v0, HalfCheetah-v2, Hopper-v2, Walker2d-v2, Humanoid-v2
    parser.add_argument('--env', help='gym name', default='CartPole-v1')
    # adagrad, rmsprop, adadelta, adam, cocob
    parser.add_argument('--optimizer', help='optimizer type name', default='adam')
    parser.add_argument('--savedir', help='save directory', default='trained_models/ppo')
    parser.add_argument('--tradir', help='trajectory directory', default='trajectory/ppo')
    parser.add_argument('--iteration', default=1000, type=int)

    return parser.parse_args()


def main(args):
    # init directories
    args.savedir = args.savedir + '/' + args.env + '/' + args.optimizer
    if not os.path.isdir(args.tradir):
        os.mkdir(args.tradir)
    if not os.path.isdir(args.tradir + '/' + args.env):
        os.mkdir(args.tradir + '/' + args.env)
    if not os.path.isdir(args.tradir + '/' + args.env + '/' + args.optimizer):
        os.mkdir(args.tradir + '/' + args.env + '/' + args.optimizer)
    args.tradir = args.tradir + '/' + args.env + '/' + args.optimizer

    # init classes
    env = gym.make(args.env)
    env.seed(0)
    ob_space = env.observation_space
    Policy = Policy_net('policy', env, args.env)
    saver = tf.train.Saver()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver.restore(sess, args.savedir + '/model.ckpt')
        obs = env.reset()
        trj_cnt = 0;
        for iteration in range(args.iteration):  # episode
            observations = []
            actions = []
            rewards = []
            run_steps = 0
            while True:
                run_steps += 1
                # prepare to feed placeholder Policy.obs
                obs = np.stack([obs]).astype(dtype=np.float32)

                act, _ = Policy.act(obs=obs, stochastic=True)
                act = np.asscalar(act)

                next_obs, reward, done, info = env.step(act)

                observations.append(obs)
                actions.append(act)
                rewards.append(reward)

                if done:
                    print('rewards:', sum(rewards))
                    obs = env.reset()
                    break
                else:
                    obs = next_obs
            if sum(rewards) >= 500:
                print('trj_cnt:', trj_cnt)
                trj_cnt += 1
                observations = np.reshape(observations, newshape=[-1] + list(ob_space.shape))
                actions = np.array(actions).astype(dtype=np.int32)

                open_file_and_save(args.tradir+'/observations.csv', observations)
                open_file_and_save(args.tradir+'/actions.csv', actions)

                if trj_cnt >= 50:
                    print('done')
                    break

if __name__ == '__main__':
    args = argparser()
    main(args)
