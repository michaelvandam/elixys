package Elixys.Validation
{
	public class EnumNumberValidation extends ValidationBase
	{
		/***
		 * Member functions
		 **/
		
		// Constructor
		public function EnumNumberValidation(sValidation:String)
		{
			// Call our base constructor
			super(sValidation);
			
			// Make sure this is the correct validation type
			if (GetValueString(TYPEKEY) != TYPE)
			{
				throw Error("Validation type mismatch");
			}
		}
		
		// Validate the value and return a string describing the first error or empty if no errors found
		public override function Validate(value:Object):String
		{
			return "";
		}
		
		// Returns the array of number values
		public function NumberValues():Array
		{
			return GetValueArray(ValidationBase.VALUEKEY);
		}
		
		/***
		 * Member variables
		 **/
		
		// Validation type
		public static var TYPE:String = "enum-number";
	}
}
