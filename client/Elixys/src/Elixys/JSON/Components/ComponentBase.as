package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	import Elixys.JSON.State.Reagent;
	
	import com.adobe.utils.StringUtil;
	
	import flash.utils.flash_proxy;
	
	public class ComponentBase extends JSONObject
	{
		// Constructor
		public function ComponentBase(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}

		// Static type
		public static function get TYPE():String
		{
			return "component";
		}

		// Data wrappers
		public function get ComponentType():String
		{
			return super.flash_proxy::getProperty("componenttype");
		}
		public function set ComponentType(value:String):void
		{
			super.flash_proxy::setProperty("componenttype", value);
		}

		public function get ID():uint
		{
			return super.flash_proxy::getProperty("id");
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}
		
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get ValidationError():Boolean
		{
			return super.flash_proxy::getProperty("validationerror");
		}
		public function set ValidationError(value:Boolean):void
		{
			super.flash_proxy::setProperty("validationerror", value);
		}
		
		// Overridden by derived classes to format additional component details
		protected function FormatComponentDetails():String
		{
			return "";
		}

		// Convert to a JSON string
		public override function toString():String
		{
			// Give our derived class a chance to format additional details
			var sAdditionalDetails:String = FormatComponentDetails();
			
			// Create a JSON response string that will be recognized by the server
			var sJSON:String = "{";
			sJSON += JSONDataString("type", Type);
			sJSON += JSONDataString("componenttype", ComponentType);
			sJSON += JSONDataString("name", Name);
			sJSON += JSONDataObject("id", ID, sAdditionalDetails != "");
			if (sAdditionalDetails != "")
			{
				sJSON += sAdditionalDetails;
			}
			sJSON += "}";
			return sJSON;
		}
		
		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			if (pComponentA.ComponentType != pComponentB.ComponentType)
			{
				return false;
			}
			if (pComponentA.ID != pComponentB.ID)
			{
				return false;
			}
			if (pComponentA.Name != pComponentB.Name)
			{
				return false;
			}
			if (pComponentA.ValidationError != pComponentB.ValidationError)
			{
				return false;
			}
			var pComponentClass:Class = Components.GetComponentClass(pComponentA.ComponentType);
			return pComponentClass.CompareComponents(pComponentA, pComponentB);
		}

		// Component array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareComponentArrays(pComponentsA:Array, pComponentsB:Array):Boolean
		{
			if (pComponentsA.length != pComponentsB.length)
			{
				return false;
			}
			else
			{
				var pComponentA:ComponentBase, pComponentB:ComponentBase;
				for (var i:int = 0; i < pComponentsB.length; ++i)
				{
					pComponentA = pComponentsA[i] as ComponentBase;
					pComponentB = pComponentsB[i] as ComponentBase;
					if (!CompareComponents(pComponentA, pComponentB))
					{
						return false;
					}
				}
			}
			return true;
		}
		
		// Overridden by derived classes to validate the component
		public function Validate():void
		{
		}

		// Validates the given field
		protected function ValidateField(pField:*, sFieldValidation:String):String
		{
			// Skip empty validation fields
			if (sFieldValidation == "")
			{
				return "";
			}

			// Create an array of key-value pairs from the validation string
			var pFields:Array = sFieldValidation.split(";");
			var pFieldValidation:Object = new Object(), sField:String, pKeyValue:Array;
			for each (sField in pFields)
			{
				pKeyValue = sField.split("=");
				pFieldValidation[StringUtil.trim(pKeyValue[0])] = StringUtil.trim(pKeyValue[1]);
			}

			// Call the appropriate validation function
			if (pFieldValidation["type"] == "enum-number")
			{
				return ValidateEnumNumber(pField, pFieldValidation);
			}
			else if (pFieldValidation["type"] == "enum-reagent")
			{
				return ValidateEnumReagent(pField, pFieldValidation);
			}
			else if (pFieldValidation["type"] == "enum-string")
			{
				return ValidateEnumString(pField, pFieldValidation);
			}
			else if (pFieldValidation["type"] == "number")
			{
				return ValidateNumber(pField, pFieldValidation);
			}
			else if (pFieldValidation["type"] == "string")
			{
				return ValidateString(pField, pFieldValidation);
			}
			else
			{
				throw Error("Unknown validation type: " + pFieldValidation["type"])
			}
		}
		
		// Validates the number enumeration
		protected function ValidateEnumNumber(pField:*, pFieldValidation:Object):String
		{
			// Handle blank values
			if (pField.toString() == "")
			{
				if (pFieldValidation["required"] == "true")
				{
					// Value required
					return "REQUIRED";
				}
				else
				{
					// Blank value is valid
					return "";
				}
			}
			
			// Make sure the value is set to one of the allowed values
			var nValue:int = parseInt(pField.toString());
			var pValues:Array = pFieldValidation["values"].split(",");
			var nIndex:int, nValidValue:int;
			for (nIndex = 0; nIndex < pValues.length; ++nIndex)
			{
				nValidValue = parseInt(pValues[nIndex].toString());
				if (nValidValue == nValue)
				{
					// Valid
					return "";
				}
			}
			
			// Any other value is invalid
			return "INVALID SELECTION";
		}
		
		// Validate the reagent enumeration
		protected function ValidateEnumReagent(pField:*, pFieldValidation:Object):String
		{
			// Handle blank values
			var pReagent:Reagent = pField as Reagent;
			if (pReagent == null)
			{
				if (pFieldValidation["required"] == "true")
				{
					// Value required
					return "REQUIRED";
				}
				else
				{
					// Blank value is valid
					return "";
				}
			}
			
			// Validate the reagent ID
			return ValidateEnumNumber(pReagent.ReagentID, pFieldValidation)
		}
		
		// Validates the string enumeration
		protected function ValidateEnumString(pField:*, pFieldValidation:Object):String
		{
			// Handle blank values
			if (pField.toString() == "")
			{
				if (pFieldValidation["required"] == "true")
				{
					// Value required
					return "REQUIRED";
				}
				else
				{
					// Blank value is valid
					return "";
				}
			}
			
			// Make sure the value is set to one of the allowed values
			var sValue:String = pField.toString();
			var pValues:Array = pFieldValidation["values"].split(",");
			var nIndex:int, sValidValue:String;
			for (nIndex = 0; nIndex < pValues.length; ++nIndex)
			{
				sValidValue = pValues[nIndex].toString();
				if (sValidValue == sValue)
				{
					// Valid
					return "";
				}
			}
			
			// Any other value is invalid
			return "INVALID SELECTION";
		}
		
		// Validates the number
		protected function ValidateNumber(pField:*, pFieldValidation:Object):String
		{
			// Handle blank values
			if (pField.toString() == "")
			{
				if (pFieldValidation["required"] == "true")
				{
					// Value required
					return "REQUIRED";
				}
				else
				{
					// Blank value is valid
					return "";
				}
			}
			
			// Make sure the number is within the acceptable range
			var nValue:Number = parseFloat(pField.toString()),
				nMin:Number = parseFloat(pFieldValidation["min"]),
				nMax:Number = parseFloat(pFieldValidation["max"]);
			if ((nValue >= nMin) && (nValue <= nMax))
			{
				return "";
			}
			else
			{
				return "OUT OF RANGE";
			}
		}
		
		// Validates the string
		protected function ValidateString(pField:*, pFieldValidation:Object):String
		{
			// Handle blank values
			if (pField.toString() == "")
			{
				if (pFieldValidation["required"] == "true")
				{
					// Value required
					return "REQUIRED";
				}
				else
				{
					// Blank value is valid
					return "";
				}
			}

			// Valid
			return "";
		}
	}
}
