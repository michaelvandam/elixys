package Elixys.Validation
{
	public class EnumReagentValidation extends ValidationBase
	{
		/***
		 * Member functions
		 **/
		
		// Constructor
		public function EnumReagentValidation(sValidation:String)
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
		
		// Returns the array of reagent IDs
		public function ReagentIDs():Array
		{
			return GetValueArray(ValidationBase.VALUEKEY);
		}
		
		/***
		 * Member variables
		 **/
		
		// Validation type
		public static var TYPE:String = "enum-reagent";
	}
}
