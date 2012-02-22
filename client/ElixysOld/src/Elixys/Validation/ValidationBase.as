package Elixys.Validation
{
	public class ValidationBase
	{
		/***
		 * Member functions
		 **/
		
		// Static class factory that create the proper derived class
		public static function CreateValidation(sValidation:String):ValidationBase
		{
			// Look up the validation type
			var sType:String = GetValueStringImpl(sValidation, TYPEKEY);
			if (sType == EnumNumberValidation.TYPE)
			{
				return new EnumNumberValidation(sValidation);
			}
			return null;
		}
		
		// Constructor
		public function ValidationBase(sValidation:String)
		{
			// Remember our validation string
			m_sValidation = sValidation;
		}
		
		// Validate the value and return a string describing the first error or empty if no errors found
		public function Validate(value:Object):String
		{
			return "";
		}
		
		// Returns the value for the given key
		protected function GetValueString(sKey:String):String
		{
			// Call the static implementation
			return GetValueStringImpl(m_sValidation, sKey);
		}
		protected function GetValueArray(sKey:String):Array
		{
			// Get the value string and split it into an array of strings
			var sValue:String = GetValueString(sKey);
			return sValue.split(",");
		}

		// Static implementation to support CreateValidation
		protected static function GetValueStringImpl(sValidation:String, sKey:String):String
		{
			// Split the validation string into key-value pairs
			var sKeyValuePairs:Array = sValidation.split("; ");
			for each (var sKeyValuePair:String in sKeyValuePairs)
			{
				// Check if the key matches the one we're looking for
				var sKeyValue:Array = sKeyValuePair.split("=");
				if (sKeyValue[0] == sKey)
				{
					// Found it
					return sKeyValue[1];
				}
			}
			
			// Key not found
			throw Error("Key not found in validation string");
		}
		
		/***
		 * Member variables
		 **/
		
		// Keys
		protected static var TYPEKEY:String = "type";
		protected static var VALUEKEY:String = "values";
		
		// Validation string
		protected var m_sValidation:String = "";
	}
}