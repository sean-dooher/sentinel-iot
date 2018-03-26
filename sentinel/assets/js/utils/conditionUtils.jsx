import {getNameFromUUID} from "./leafUtils";

export function predicateToString(predicate, leaves, not=false, tab=0) {
    let tabs = ' '.repeat(tab);
    let connectors = {
        'AND': 'and',
        'OR': 'or',
        'xor': 'xor',
        'NOT': 'not'
    };

    if(!(predicate instanceof Array))
        return predicate;

    if(predicate.length === 2 && !(predicate[0] in connectors))
        return '<' + getNameFromUUID(predicate[0], leaves) + ', ' + predicate[1] + '>';

    if(predicate[0] === 'NOT')
        return tabs + predicateToString(predicate[1], leaves, true, tab+2);

    if(predicate[0] in connectors){
        let result = '';
        for(let subPredicate of predicate[1]) {
            result += predicateToString(subPredicate, leaves, tab=tab+2);
            result += '\n' + connectors[predicate[0]] + '\n';
        }
        result = result.slice(0, -(2 + predicate[0].length));
        if(not)
            return 'not (' + result + ')';
        else
            return result;
    }

    let operators;
    if(!not) {
        operators = {
            '=': ' equals ',
            '>': ' greater than ',
            '<': ' less than ',
        };
    } else {
        operators = {
            '=': ' does not equal ',
            '>': ' is not greater than ',
            '<': ' is not less than ',
        };
    }

    if(predicate[0] in operators)
        return tabs + predicateToString(predicate[1], leaves, not, tab) + operators[predicate[0]] + predicateToString(predicate[2], leaves, not, tab);

    return predicate;
}