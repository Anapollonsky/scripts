import java.util.*;
import java.math.*;

public class euler {
	static int maxnumprimes = (int) Math.pow(10, 3);
	static int maxnumfib = (int) Math.pow(10, 3);
	static ArrayList<Integer> primes = (ArrayList) listprimes(maxnumprimes);
	
	// Generate a list of primes up to a maximum number
	static List<Integer> listprimes(Integer maxnum){
		ArrayList<Integer> primesout = new ArrayList<Integer>();
		primesout.add(2);
		for (int i = 3; i < maxnum; i ++){
			int temp = 0;
			for (Integer theint: primesout){
				if (i % theint == 0) {
					temp = 1;
					break;
				}
			}
			if (temp == 0){
				primesout.add(i);
			}
		}
		return primesout;
	}
	
	// Check if a number is prime
	static boolean isprime(int theint){
		if (theint < maxnumprimes) {
			return primes.contains(theint);	 
		} else  {
			for (int newint: primes) {
				if (theint % newint == 0){
					return false;
				}
			}
			if (theint > Math.pow(maxnumprimes, 2))
				for (int i = maxnumprimes + 1; i < Math.sqrt(theint); i++) {
					if (theint % i == 0){
						return false;
					}
				}
			return true;
		}
	}
	
	// Strip the duplicates from a list of 
	static List<Integer> stripduplicates(List<Integer> thelist){
		HashSet<Integer> theset = new HashSet<Integer>(thelist);
		return new ArrayList<Integer>(theset);
	}
	
	static List<Integer> genfibonacci(int maxnum){
		ArrayList<Integer> outputlist = new ArrayList<Integer>(Arrays.asList(1, 1));
		int a = 1;
		int b = 1;
		int c;
		while(a < maxnum){
			c = a + b;
			outputlist.add(c);
			a = b;
			b = c;
		}
		return outputlist;
	}
	
	// 52
	static boolean samedigits(int a, int b){
		int intlen = String.valueOf(a).length();
		if ( intlen != String.valueOf(b).length()){
			return false;
		}
		ArrayList<Integer> lista = new ArrayList<Integer>(intlen);
		ArrayList<Integer> listb = new ArrayList<Integer>(intlen);
		int atemp = a;
		int btemp = b;
		for (int i = 0; i < intlen; i++){
			lista.add(atemp % 10);
			listb.add(btemp % 10);
			atemp /= 10;
			btemp /= 10;
		}
		Collections.sort(lista);
		Collections.sort(listb);
		if (lista.equals(listb)){
			return true;
		}
		return false;
	}
	
	static int num52(int maxnum){
		for (int i = 1; i < maxnum; i++){
			if (samedigits(i, 2*i) && samedigits (i, 3*i) && samedigits(i, 4*i) && samedigits(i, 5*i) && samedigits(i, 6*i)) {
				return i;
			}
		}
		return 0;
	}
	
	// 55
	static int reverseint(int toreverse){
		int reversedNum = 0;
		while (toreverse != 0) {
		    reversedNum = reversedNum * 10 + toreverse % 10;
		    toreverse = toreverse / 10;   
		}
		return reversedNum;
	}
	
	static boolean ispalindrome(int input){
		String inputstring = String.valueOf(input);
		for (int i = 0; i < inputstring.length()/2; i++){
			if (inputstring.charAt(i) != inputstring.charAt(inputstring.length()-i-1)) {
				return false;
			}
		}
		return true;
	}
	
	static boolean islychrel(int num){
		for (int i = 0; i < 50; i++){
			num = num + reverseint(num);
			if (ispalindrome(num)){
				return false;
			}
		}
		return true;
	}
	
	static int num55(int maxint){
		int accu = 0;
		for (int i = 1; i < maxint; i++){
			if (islychrel(i)){
				accu++;
			}
		}
		return accu;
	}
	
	// 60
	/*
	static ArrayList<Integer> num60(){
		for (Integer i: primes){
			
		}
	}
	*/
	
	static boolean allprime(ArrayList<Integer> inlist){
		for (int i: inlist){
			if (!isprime(i)){
				return false;
			}
		}
		return true;
	}
		
	static int concatints(int a, int b){
		return (int) (b + a * Math.pow(10, String.valueOf(b).length()));
	}
		
	/*
	static boolean pairconcatprime(ArrayList<Integer> thelist){
		
	}
	*/
	
	public static void main(String[] args) {
		System.out.println(isprime(5));
		
		ArrayList<Integer> places = new ArrayList<Integer>(Arrays.asList(1, 3, 5, 3));
		System.out.println(genfibonacci(maxnumfib).toString());
		System.out.println(islychrel(47));
		System.out.println(num55(100000));
	}

}
