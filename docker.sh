#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  图书推荐系统 - Docker管理脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "使用方法: ./docker.sh [命令]"
    echo ""
    echo "可用命令:"
    echo -e "  ${GREEN}start${NC}      启动所有服务"
    echo -e "  ${GREEN}stop${NC}       停止所有服务"
    echo -e "  ${GREEN}restart${NC}    重启所有服务"
    echo -e "  ${GREEN}status${NC}     查看服务状态"
    echo -e "  ${GREEN}logs${NC}       查看实时日志"
    echo -e "  ${GREEN}build${NC}      重新构建镜像"
    echo -e "  ${GREEN}clean${NC}      清理所有容器和镜像"
    echo -e "  ${GREEN}update${NC}     更新并重启服务"
    echo -e "  ${GREEN}help${NC}       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./docker.sh start          # 启动服务"
    echo "  ./docker.sh logs frontend  # 查看前端日志"
    echo "  ./docker.sh stop           # 停止服务"
    echo ""
}

# 检查Docker环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[错误] 未检测到Docker，请先安装Docker${NC}"
        echo "安装文档: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}[错误] 未检测到Docker Compose，请先安装${NC}"
        echo "安装文档: https://docs.docker.com/compose/install/"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}[错误] Docker服务未启动，请先启动Docker${NC}"
        exit 1
    fi

    echo -e "${GREEN}[✓] Docker环境检查通过${NC}"
}

# 检查.env文件
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}[提示] 未找到.env文件，使用.env.example创建默认配置${NC}"
        cp .env.example .env
        echo -e "${GREEN}[✓] 已创建.env文件${NC}"
    fi
}

# 启动服务
start_services() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  启动图书推荐系统${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    check_docker
    check_env

    echo -e "${YELLOW}[1/3] 构建Docker镜像...${NC}"
    docker-compose build

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 镜像构建失败${NC}"
        exit 1
    fi

    echo -e "${YELLOW}[2/3] 启动所有服务...${NC}"
    docker-compose up -d

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 容器启动失败${NC}"
        exit 1
    fi

    echo -e "${YELLOW}[3/3] 等待服务就绪...${NC}"
    sleep 5

    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  部署完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}服务访问地址:${NC}"
    echo -e "  🌐 前端界面:     ${BLUE}http://localhost${NC}"
    echo -e "  🔌 后端API:      ${BLUE}http://localhost:8080${NC}"
    echo -e "  🤖 算法服务:     ${BLUE}http://localhost:5000${NC}"
    echo -e "  🗄️  MySQL数据库:  ${BLUE}116.205.244.106:3306${NC} (远程)"
    echo ""
    echo -e "${GREEN}常用命令:${NC}"
    echo -e "  查看状态:  ${YELLOW}./docker.sh status${NC}"
    echo -e "  查看日志:  ${YELLOW}./docker.sh logs${NC}"
    echo -e "  停止服务:  ${YELLOW}./docker.sh stop${NC}"
    echo ""

    # 显示容器状态
    echo -e "${GREEN}容器运行状态:${NC}"
    docker-compose ps
    echo ""
}

# 停止服务
stop_services() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}  停止图书推荐系统${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    echo -e "${YELLOW}正在停止所有服务...${NC}"
    docker-compose stop

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 停止失败${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  所有服务已停止${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}提示:${NC}"
    echo -e "  重新启动: ${GREEN}./docker.sh start${NC}"
    echo -e "  完全清理: ${GREEN}./docker.sh clean${NC}"
    echo ""
}

# 重启服务
restart_services() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}  重启图书推荐系统${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    echo -e "${YELLOW}正在重启所有服务...${NC}"
    docker-compose restart

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 重启失败${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  所有服务已重启${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    # 显示容器状态
    docker-compose ps
    echo ""
}

# 查看服务状态
show_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  服务运行状态${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    docker-compose ps

    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  资源使用情况${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        book-recommendation-frontend \
        book-recommendation-backend \
        book-recommendation-algorithm 2>/dev/null || echo "容器未运行"

    echo ""
}

# 查看日志
view_logs() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  查看实时日志${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}提示: 按 Ctrl+C 退出日志查看${NC}"
    echo ""

    if [ -z "$1" ]; then
        # 查看所有服务日志
        docker-compose logs -f
    else
        # 查看特定服务日志
        docker-compose logs -f "$1"
    fi
}

# 重新构建
rebuild_services() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}  重新构建镜像${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    echo -e "${YELLOW}正在重新构建所有镜像...${NC}"
    docker-compose build --no-cache

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 构建失败${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}[✓] 构建完成${NC}"
    echo ""
    echo -e "${YELLOW}是否立即重启服务？[y/N]${NC} "
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        restart_services
    fi
}

# 清理所有资源
clean_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${RED}  清理所有Docker资源${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${RED}警告: 此操作将删除所有容器、镜像和数据卷（不包括远程MySQL数据）${NC}"
    echo -e "${YELLOW}是否继续？[y/N]${NC} "
    read -r response

    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${GREEN}已取消操作${NC}"
        exit 0
    fi

    echo ""
    echo -e "${YELLOW}[1/4] 停止并删除所有容器...${NC}"
    docker-compose down -v

    echo -e "${YELLOW}[2/4] 删除相关镜像...${NC}"
    docker images | grep book-recommendation | awk '{print $3}' | xargs -r docker rmi -f

    echo -e "${YELLOW}[3/4] 清理未使用的镜像...${NC}"
    docker image prune -f

    echo -e "${YELLOW}[4/4] 清理未使用的卷...${NC}"
    docker volume prune -f

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  清理完成${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# 更新并重启
update_services() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  更新系统${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    echo -e "${YELLOW}[1/3] 停止服务...${NC}"
    docker-compose down

    echo -e "${YELLOW}[2/3] 重新构建镜像...${NC}"
    docker-compose build --no-cache

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 构建失败${NC}"
        exit 1
    fi

    echo -e "${YELLOW}[3/3] 启动服务...${NC}"
    docker-compose up -d

    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 启动失败${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  更新完成${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    docker-compose ps
    echo ""
}

# 主逻辑
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        view_logs "$2"
        ;;
    build)
        rebuild_services
        ;;
    clean)
        clean_all
        ;;
    update)
        update_services
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}[错误] 未知命令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
