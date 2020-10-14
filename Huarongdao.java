import java.util.ArrayList;
import java.util.List;

public class Huarongdao{
	//每走一步，棋盘状态发生变化，生产一个新的棋盘，棋盘列表就构成了走棋的步骤
	public final static int MAX_X=4;
	public final static int MAX_Y=5;
	public final int DEST_X=2;
	public final int DEST_Y=1;
	public static Board startBoard;

	public static List<Board> boardList = new ArrayList<>();	
	public List<Solution> solutionList = new ArrayList<>();
	public int bestSteps = 100;

	public static void main(String[] args) throws Exception{
		Huarongdao huarongdao = new Huarongdao();
		huarongdao.initBoard();
		huarongdao.moveNextStep();
		huarongdao.printBestSolution();
	}
	public void printBestSolution(){
		int minStep = 10000;
		int index = -1;
		for(int i=0; i<solutionList.size(); i++){
			if (solutionList.get(i).getSteps() < minStep){
				minStep = solutionList.get(i).getSteps();
				index = i;
			}
		}
		if (index >= 0){
			System.out.println(String.format("最小步数：%d",minStep));
			solutionList.get(index).printSolution();
		}

	}
	public static void debug(String line){
		//System.out.println(line);
		return;
	}
	public static String getDirectionName(int direction){
		switch(direction){
			case Role.DIRECTION_UP:
				return "UP";
			case Role.DIRECTION_DOWN:
				return "DOWN";
			case Role.DIRECTION_LEFT:
				return "LEFT";
			case Role.DIRECTION_RIGHT:
				return "RIGHT";
			default:
				System.out.println("unknow direction");
				return "UNKNOWN";
		}
	}
	public static Boolean isOutOfBoard(Location location){
		if (location.x > MAX_X || location.x <= 0 || location.y > MAX_Y || location.y <= 0){
				return true;
		}else{
				return false;
		}
	}
	public void initBoard(){
		//命名规则：竖长方形为将，横长方形为帅
		Role[] roles = new Role[10];
		/*
		roles[0] = new Role("曹操",Role.ROLE_CAOCHAO,new Location(3,2));
		roles[1] = new Role("将一",Role.ROLE_VERTICAL,new Location(1,2));
		roles[2] = new Role("将二",Role.ROLE_VERTICAL,new Location(2,2));
		roles[3] = new Role("将三",Role.ROLE_VERTICAL,new Location(1,4));
		roles[4] = new Role("将四",Role.ROLE_VERTICAL,new Location(2,4));
		roles[5] = new Role("将五",Role.ROLE_VERTICAL,new Location(4,4));
		roles[6] = new Role("兵一",Role.ROLE_SOLDIER,new Location(1,1));
		roles[7] = new Role("兵二",Role.ROLE_SOLDIER,new Location(2,1));
		roles[8] = new Role("兵三",Role.ROLE_SOLDIER,new Location(3,1));
		roles[9] = new Role("兵四",Role.ROLE_SOLDIER,new Location(4,1));
		roles[0] = new Role("曹操",Role.ROLE_CAOCHAO,new Location(2,2));
		roles[1] = new Role("将一",Role.ROLE_VERTICAL,new Location(1,3));
		roles[2] = new Role("帅一",Role.ROLE_HORIZON,new Location(1,1));
		roles[3] = new Role("帅二",Role.ROLE_HORIZON,new Location(3,1));
		roles[4] = new Role("帅三",Role.ROLE_HORIZON,new Location(1,5));
		roles[5] = new Role("帅四",Role.ROLE_HORIZON,new Location(3,5));
		roles[6] = new Role("兵一",Role.ROLE_SOLDIER,new Location(1,2));
		roles[7] = new Role("兵二",Role.ROLE_SOLDIER,new Location(4,2));
		roles[8] = new Role("兵三",Role.ROLE_SOLDIER,new Location(4,3));
		roles[9] = new Role("兵四",Role.ROLE_SOLDIER,new Location(4,4));
		roles[0] = new Role("曹操",Role.ROLE_CAOCHAO,new Location(2,3));
		roles[1] = new Role("将一",Role.ROLE_VERTICAL,new Location(1,2));
		roles[2] = new Role("将二",Role.ROLE_VERTICAL,new Location(3,1));
		roles[3] = new Role("将三",Role.ROLE_VERTICAL,new Location(1,4));
		roles[4] = new Role("将四",Role.ROLE_VERTICAL,new Location(4,3));
		roles[5] = new Role("帅一",Role.ROLE_HORIZON,new Location(2,5));
		roles[6] = new Role("兵一",Role.ROLE_SOLDIER,new Location(2,1));
		roles[7] = new Role("兵二",Role.ROLE_SOLDIER,new Location(2,2));
		roles[8] = new Role("兵三",Role.ROLE_SOLDIER,new Location(4,2));
		roles[9] = new Role("兵四",Role.ROLE_SOLDIER,new Location(4,5));
		*/
		roles[0] = new Role("曹操",Role.ROLE_CAOCHAO,new Location(1,4));
		roles[1] = new Role("将一",Role.ROLE_VERTICAL,new Location(1,1));
		roles[2] = new Role("将二",Role.ROLE_VERTICAL,new Location(2,1));
		roles[3] = new Role("将三",Role.ROLE_VERTICAL,new Location(4,1));
		roles[4] = new Role("帅一",Role.ROLE_HORIZON,new Location(3,4));
		roles[5] = new Role("帅二",Role.ROLE_HORIZON,new Location(3,5));
		roles[6] = new Role("兵一",Role.ROLE_SOLDIER,new Location(3,1));
		roles[7] = new Role("兵二",Role.ROLE_SOLDIER,new Location(3,2));
		roles[8] = new Role("兵三",Role.ROLE_SOLDIER,new Location(3,3));
		roles[9] = new Role("兵四",Role.ROLE_SOLDIER,new Location(4,3));
		startBoard = new Board(roles);
		boardList.add(startBoard);
		startBoard.printRole();
		startBoard.printBoard();
	}
	public Boolean isSuccess(Board board){
		for(int i=0; i<board.roles.length; i++){
			if (board.roles[i].type != Role.ROLE_CAOCHAO) { continue; }
			if (board.roles[i].location.x == DEST_X && board.roles[i].location.y == DEST_Y){
				return true;
			}else{
				return false;
			}
		}
		System.out.println("can not find caochao");
		return false;
	}	

	public void pushBoard(Board board){
			int i=boardList.size()-1;
			String name = boardList.get(i).getNextStepName();
			String direction = boardList.get(i).getNextStepDirection();
			debug(String.format("%s move %s",name,direction));
		Board newBoard = board;
		boardList.add(newBoard);	
	}
	public void popBoard(){
		debug("back");
		boardList.remove(boardList.size()-1);
	}
	public Board currentBoard(){
		return boardList.get(boardList.size()-1);
	}
	public Boolean isNewBoard(Board board){
		//非空，且和已有棋盘列表中的棋盘不重复，就返回true
		if (board == null) { return false; }

		for(int i=0; i<boardList.size(); i++){
			if (isSameBoard(boardList.get(i),board)) { return false; }
		}
		debug("it is a new board");
		return true;
	}
	public Boolean isSameBoard(Board board1,Board board2){
		//
		//board1.printBoard();
		//board2.printBoard();
		for(int i=0; i<board1.roles.length; i++){
			Boolean haveSameRole = false;
			//在board2找和它相同的roles
			for(int j=0; j<board2.roles.length; j++){
				if (board1.roles[i].type == board2.roles[j].type
								&& board1.roles[i].location.x == board2.roles[j].location.x
								&& board1.roles[i].location.y == board2.roles[j].location.y){
					haveSameRole = true;
					break;
				}
			}
			if (haveSameRole == false)  {return false;}
		}
		debug("board is same");
		return true;
	}

	public Boolean moveNextStep(){
		//获取当前棋盘,并
		Board board = currentBoard();
		if(isSuccess(board)){
			//printStep();
			//return true;	
			//把当前步骤记录下来，继续执行，寻找其他解法
			Solution solution = new Solution(boardList);
			if (solution.getSteps() < bestSteps){
				bestSteps = solution.getSteps();
				solutionList.add( solution);
				solutionList.get(solutionList.size()-1).printSolution();
			}
			popBoard();
			return false;
		}

		if (boardList.size() >= bestSteps){
			//已经超出最优步骤，回退
			popBoard();
			return false;
		}
		//currentBoard().printBoard();
		
		for(int i=0; i<board.roles.length; i++){
			Board nextBoard;
			//向上
			nextBoard = board.move(i,Role.DIRECTION_UP);
			if (isNewBoard(nextBoard)){  //如果非空且不重复，也即新的棋盘
				pushBoard(nextBoard);    //加入步骤，并递归移动下一步
				if (moveNextStep()) { return true; }	
			}		
			//向下
			nextBoard = board.move(i,Role.DIRECTION_DOWN);
			if (isNewBoard(nextBoard)){
				pushBoard(nextBoard);
				if (moveNextStep()) { return true; }	
			}		
			//向左
			nextBoard = board.move(i,Role.DIRECTION_LEFT);
			if (isNewBoard(nextBoard)){
				pushBoard(nextBoard);
				if (moveNextStep()) { return true; }	
			}		
			//向右
			nextBoard = board.move(i,Role.DIRECTION_RIGHT);
			if (isNewBoard(nextBoard)){
				pushBoard(nextBoard);
				if (moveNextStep()) { return true; }	
			}		
		}
		popBoard();
		return false;

		/*
		Location location ;
	    location = 	new Location(1,1);
		Role role ;
		role = new Role(Role.ROLE_CAOCHAO,location);
		Location[] spaceLocation;
		spaceLocation = role.needSpaceForMove(Role.DIRECTION_UP);
		for(int i=0; i < spaceLocation.length; i++){
			System.out.println("X:"+String.valueOf(spaceLocation[i].x));
			System.out.println("Y:"+String.valueOf(spaceLocation[i].y));
		}
		*/
	}
	public void printStep(){
		System.out.println("步骤如下：");
		for(int i=0; i<boardList.size(); i++){
			String name = boardList.get(i).getNextStepName();
			String direction = boardList.get(i).getNextStepDirection();
			System.out.println(String.format("%s move %s",name,direction));
		}
		System.out.println(String.format("total step:%d",boardList.size()-1));
	}

	
	//棋盘，所有棋子的位置,构成了棋盘
	class Board{
		//当前所有棋子及位置
		public Role[] roles;
		//每走一步，记录下棋子的序号和方向
		public int nextStepIndexOfRole=-1;
		public int nextStepDirection=-1;

		Board(Role[] roles){
			this.roles = roles;
		}
		public Board move(int indexOfRole,int direction){
			//如果可行，就返回走完一步后新的棋盘，否则就返回null
			
			//检查是否可移动	
			if (!canBeMoved(indexOfRole,direction)){
				debug(String.format("%s:%s N",roles[indexOfRole].name,getDirectionName(direction)));
				return null;
			}
			debug(String.format("%s:%s Y",roles[indexOfRole].name,getDirectionName(direction)));
			//记录移动步骤
			nextStepIndexOfRole = indexOfRole;
			nextStepDirection = direction;
			//生成新的棋盘
			return newBoardAfterMove(indexOfRole,direction);
		}
		public Board newBoardAfterMove(int indexOfRole,int direction){
			//按照指定方向移动指定索引的棋子后，生成新的棋盘
			//复制棋盘的roles
			Role[] newRoles = new Role[roles.length];
			for (int i=0; i<roles.length; i++){
				newRoles[i] = new Role(roles[i].name,roles[i].type,new Location(roles[i].location.x,roles[i].location.y));
			}
			//移动的role，更新位置
			switch(direction){
				case Role.DIRECTION_UP:
					newRoles[indexOfRole].location.y += 1;
					break;
				case Role.DIRECTION_DOWN:
					newRoles[indexOfRole].location.y -= 1;
					break;
				case Role.DIRECTION_LEFT:
					newRoles[indexOfRole].location.x -= 1;
					break;
				case Role.DIRECTION_RIGHT:
					newRoles[indexOfRole].location.x += 1;
					break;
				default:
					System.out.println("error:unknown direction"+String.valueOf(direction));
			}
			//新的role位置组成新的棋盘
			//return new Board(newRoles);

			Board newBoard = new Board(newRoles);
			//newBoard.printBoard();
			return newBoard;
		}
		public void printRole(){
			for(int i=0; i<roles.length; i++){
				System.out.println(String.format("%s:%d,%d",roles[i].name,roles[i].location.x,roles[i].location.y));
			}
		}
		public void printBoard(){
			System.out.println("当前棋盘:");
			for(int y=MAX_Y; y>=1; y--){
				String line = "";
				for(int x=1; x<=MAX_X; x++){
					line = line + getCharOfLocation(new Location(x,y));
				}
				System.out.println(line);
			}
		}

		public Boolean canBeMoved(int indexOfRole,int direction){
			Location[] needEmptyLocations = roles[indexOfRole].needSpaceForMove(direction);
			for(int i=0; i<needEmptyLocations.length; i++){
				if (isOutOfBoard(needEmptyLocations[i])) { return false; }
				if (isEmpty(needEmptyLocations[i]) == false){
					return false;	
				}
			}
			return true;
		}
		public Boolean isEmpty(Location location){
			for(int i=0; i<roles.length; i++){
				if (roles[i].isOccupied(location)){
					return false;
				}
			}
			return true;
		}
		public String getNextStepName() {
			if (nextStepIndexOfRole == -1){
					return "";
			}
			return roles[nextStepIndexOfRole].name;
		}
		public String getNextStepDirection(){
			switch(nextStepDirection){
				case Role.DIRECTION_UP:
					return "UP";
				case Role.DIRECTION_DOWN:
					return "DOWN";
				case Role.DIRECTION_LEFT:
					return "LEFT";
				case Role.DIRECTION_RIGHT:
					return "RIGHT";
				default:
					return "";
			}
		}
		public String getCharOfLocation(Location location){
			for(int i=0; i<roles.length; i++){
				if (roles[i].isOccupied(location)){
					return (roles[i].name.subSequence(0,1)).toString();
				}
			}
			return "空";
		}
	}
	//棋子
	class Role{
		//四种棋子
		public final static int ROLE_CAOCHAO = 0;  //占4格
		public final static int ROLE_SOLDIER = 1;  //占一格
		public final static int ROLE_HORIZON = 2;  //水平的长方形，占2格
		public final static int ROLE_VERTICAL = 3; //垂直的长方形，占2格

		public final static int DIRECTION_UP = 0;
		public final static int DIRECTION_DOWN = 1;
		public final static int DIRECTION_LEFT = 2;
		public final static int DIRECTION_RIGHT = 3;

		public String name; 
		public int type;
		public Location location; //以左下角的坐标来记录棋子的位置
		
		Role(String name,int type,Location location){
			this.name = name;
			this.type = type;
			this.location = location;
		}
		Location[] needSpaceForMove(int direction){
			switch(type){
				case ROLE_CAOCHAO:
					switch(direction){
						case DIRECTION_UP:
							return new Location[]{new Location(location.x,  location.y+2),
												  new Location(location.x+1,location.y+2)};
						case DIRECTION_DOWN:
							return new Location[]{new Location(location.x,  location.y-1),
												  new Location(location.x+1,location.y-1)};
						case DIRECTION_LEFT:
							return new Location[]{new Location(location.x-1,location.y),
												  new Location(location.x-1,location.y+1)};
						case DIRECTION_RIGHT:
							return new Location[]{new Location(location.x+2,location.y),
												  new Location(location.x+2,location.y+1)};
						default:
							System.out.println("error:unknown direction"+String.valueOf(direction));
					}
				case ROLE_SOLDIER:
					switch(direction){
						case DIRECTION_UP:
							return new Location[]{new Location(location.x,  location.y+1)};
						case DIRECTION_DOWN:
							return new Location[]{new Location(location.x,  location.y-1)};
						case DIRECTION_LEFT:
							return new Location[]{new Location(location.x-1,location.y)};
						case DIRECTION_RIGHT:
							return new Location[]{new Location(location.x+1,location.y)};
						default:
							System.out.println("error:unknown direction"+String.valueOf(direction));
					}
				case ROLE_HORIZON:
					switch(direction){
						case DIRECTION_UP:
							return new Location[]{new Location(location.x,  location.y+1),
												  new Location(location.x+1,location.y+1)};
						case DIRECTION_DOWN:
							return new Location[]{new Location(location.x,  location.y-1),
												  new Location(location.x+1,location.y-1)};
						case DIRECTION_LEFT:
							return new Location[]{new Location(location.x-1,  location.y)};
						case DIRECTION_RIGHT:
							return new Location[]{new Location(location.x+2,  location.y)};
						default:
							System.out.println("error:unknown direction"+String.valueOf(direction));
					}
				case ROLE_VERTICAL:
					switch(direction){
						case DIRECTION_UP:
							return new Location[]{new Location(location.x,  location.y+2)};
						case DIRECTION_DOWN:
							return new Location[]{new Location(location.x,  location.y-1)};
						case DIRECTION_LEFT:
							return new Location[]{new Location(location.x-1,location.y),
												  new Location(location.x-1,location.y+1)};
						case DIRECTION_RIGHT:
							return new Location[]{new Location(location.x+1,location.y),
												  new Location(location.x+1,location.y+1)};
						default:
							System.out.println("error:unknown direction"+String.valueOf(direction));
					}
				default:
					System.out.println("error:unknown type"+String.valueOf(type));
			}
			return null;
		}
		public Boolean isOccupied(Location location){
			switch(type){
				case ROLE_CAOCHAO:
					if ((location.x == this.location.x || location.x == this.location.x+1)
							&& (location.y == this.location.y || location.y == this.location.y+1)){
						return true;
					}
					return false;
				case ROLE_SOLDIER:
					if (location.x == this.location.x && location.y == this.location.y){
						return true;
					}
					return false;
				case ROLE_HORIZON:
					if ((location.x == this.location.x || location.x == this.location.x+1) && location.y == this.location.y){
						return true;
					}
					return false;
				case ROLE_VERTICAL:
					if (location.x == this.location.x && (location.y == this.location.y || location.y == this.location.y+1)){
						return true;
					}
					return false;
				default:
					System.out.println("error:unknown type"+String.valueOf(type));
					return false;
			}
		}
	}
	class Location{
		int x;
		int y;
		Location(int x,int y){
			this.x = x;
			this.y = y;
		}
	}
	class Solution{
		List<String> stepList = new ArrayList<>();

		Solution(List<Board> boardList){
			if (boardList == null){
				debug("boardList is null");
				return;
			}
			for (int i=0; i<boardList.size()-1; i++){
				String name = boardList.get(i).getNextStepName();
				String direction = boardList.get(i).getNextStepDirection();
				stepList.add(String.format("%s : %s",name,direction));
			}
			//printSolution();
		}
		public void printSolution(){
			System.out.println(String.format("解法共%d步：",stepList.size()));
			for(int i=0; i<stepList.size(); i++){
				System.out.println(stepList.get(i));
			}
		}
		public int getSteps() { return stepList.size(); }
	}
}


