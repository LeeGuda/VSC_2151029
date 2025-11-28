import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import matplotlib.pyplot as plt
import pickle
import os
import subprocess
from multiprocessing import Process

# 테트로미노 블록 정의
TETROMINOS = [
    np.array([[1, 1, 1, 1]]),                # I
    np.array([[1, 1], [1, 1]]),              # O
    np.array([[0, 1, 0], [1, 1, 1]]),        # T
    np.array([[0, 1, 1], [1, 1, 0]]),        # S
    np.array([[1, 1, 0], [0, 1, 1]]),        # Z
    np.array([[1, 0, 0], [1, 1, 1]]),        # J
    np.array([[0, 0, 1], [1, 1, 1]])         # L
]

# 테트리스 환경 (간단 버전)
class TetrisEnv:
    def __init__(self):
        self.height = 20
        self.width = 10
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.score = 0
        self.done = False
        self.current_block = None
        self.block_pos = [0, 3]  # 시작 위치 (row, col)

    def reset(self):
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.score = 0
        self.done = False
        self.spawn_block()
        return self.board.copy()

    def spawn_block(self):
        self.current_block = random.choice(TETROMINOS)
        self.block_pos = [0, (self.width - self.current_block.shape[1]) // 2]
        if self.check_collision(self.current_block, self.block_pos):
            self.done = True

    def check_collision(self, block, pos):
        r, c = pos
        for i in range(block.shape[0]):
            for j in range(block.shape[1]):
                if block[i, j]:
                    if r + i >= self.height or c + j < 0 or c + j >= self.width:
                        return True
                    if self.board[r + i, c + j]:
                        return True
        return False

    def fix_block(self):
        r, c = self.block_pos
        for i in range(self.current_block.shape[0]):
            for j in range(self.current_block.shape[1]):
                if self.current_block[i, j]:
                    self.board[r + i, c + j] = 1

    def clear_lines(self):
        lines_cleared = 0
        new_board = self.board.copy()
        for i in range(self.height):
            if np.all(self.board[i, :] == 1):
                new_board[1:i+1, :] = new_board[0:i, :]
                new_board[0, :] = 0
                lines_cleared += 1
        self.board = new_board
        return lines_cleared

    def step(self, action):
        # action: 0=좌, 1=우, 2=회전, 3=아래(드롭)
        reward = 0
        block = self.current_block.copy()
        pos = self.block_pos.copy()
        if action == 0:  # 좌
            pos[1] -= 1
            if not self.check_collision(block, pos):
                self.block_pos = pos
        elif action == 1:  # 우
            pos[1] += 1
            if not self.check_collision(block, pos):
                self.block_pos = pos
        elif action == 2:  # 회전
            block = np.rot90(block)
            if not self.check_collision(block, self.block_pos):
                self.current_block = block
        # 아래(드롭)
        down_pos = [self.block_pos[0] + 1, self.block_pos[1]]
        if not self.check_collision(self.current_block, down_pos):
            self.block_pos = down_pos
        else:
            self.fix_block()
            lines = self.clear_lines()
            reward = lines
            self.score += reward
            self.spawn_block()
        if self.done:
            return self.board.copy(), reward, True, {}
        return self.board.copy(), reward, False, {}

    def render(self):
        temp_board = self.board.copy()
        r, c = self.block_pos
        for i in range(self.current_block.shape[0]):
            for j in range(self.current_block.shape[1]):
                if self.current_block[i, j]:
                    if 0 <= r + i < self.height and 0 <= c + j < self.width:
                        temp_board[r + i, c + j] = 2  # 현재 블록은 2로 표시
        plt.imshow(temp_board, cmap='gray')
        plt.title('Tetris Board')
        plt.axis('off')
        plt.show()

# DQN 네트워크
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    def forward(self, x):
        return self.fc(x)

# DQN 에이전트
class DQNAgent:
    def __init__(self, state_dim, action_dim):
        self.model = DQN(state_dim, action_dim)
        self.target_model = DQN(state_dim, action_dim)
        self.target_model.load_state_dict(self.model.state_dict())
        self.memory = deque(maxlen=10000)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        self.batch_size = 64

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return random.randrange(4)  # action space: 0~3
        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.model(state)
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        if len(self.memory) < self.batch_size:
            return
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)

        q_values = self.model(states)
        next_q_values = self.target_model(next_states)
        q_value = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        next_q_value = next_q_values.max(1)[0]
        expected_q = rewards + self.gamma * next_q_value * (1 - dones)

        loss = nn.MSELoss()(q_value, expected_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target(self):
        self.target_model.load_state_dict(self.model.state_dict())

if __name__ == "__main__":
    # 모든 경험 데이터 통합
    import pickle, glob
    from collections import deque
    max_memory = 10000000  # 최대 1천만개까지 저장 (RAM 16GB 기준)
    unified_memory = deque(maxlen=max_memory)
    for exp_file in glob.glob("experience_*.pkl"):
        with open(exp_file, "rb") as f:
            data = pickle.load(f)
            unified_memory.extend(data)
    print(f"Unified experience memory loaded: {len(unified_memory)} samples.")

    num_procs = 8
    procs = []
    def train_tetris_agent(proc_id, episodes=250, shared_memory=None):
        device = torch.device('cpu')
        env = TetrisEnv()
        state_dim = env.board.size
        action_dim = 4
        agent = DQNAgent(state_dim, action_dim)
        agent.model.to(device)
        agent.target_model.to(device)
        # 통합 경험 데이터로 시작
        if shared_memory is not None:
            agent.memory = deque(shared_memory, maxlen=max_memory)
        # 모델 및 경험 데이터 불러오기 (각 프로세스별 파일명 분리)
        model_path = f"best_model_{proc_id}.pth"
        exp_path = f"experience_{proc_id}.pkl"
        if os.path.exists(model_path):
            agent.model.load_state_dict(torch.load(model_path))
        if os.path.exists(exp_path):
            with open(exp_path, "rb") as f:
                agent.memory.extend(pickle.load(f))
        best_reward = -float('inf')
        for ep in range(episodes):
            state = env.reset().flatten()
            total_reward = 0
            for t in range(500):
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
                action = agent.act(state)
                next_state, reward, done, _ = env.step(action)
                next_state = next_state.flatten()
                agent.remember(state, action, reward, next_state, done)
                agent.train()
                state = next_state
                total_reward += reward
                if done:
                    break
            # 최고 리워드 갱신 시만 저장
            if total_reward > best_reward:
                best_reward = total_reward
                torch.save(agent.model.state_dict(), model_path)
                with open(exp_path, "wb") as f:
                    pickle.dump(agent.memory, f)
                print(f"Process {proc_id}: Best model & experience saved at episode {ep}, reward {best_reward}")
                import subprocess
                subprocess.run(["git", "add", model_path, exp_path])
                subprocess.run(["git", "commit", "-m", f"Proc {proc_id}: Update best model & experience at episode {ep}, reward {best_reward}"])
                subprocess.run(["git", "push"])
        print(f"Process {proc_id} finished.")

    for i in range(num_procs):
        p = Process(target=train_tetris_agent, args=(i, 250, unified_memory))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
